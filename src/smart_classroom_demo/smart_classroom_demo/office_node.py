from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .message_utils import build_payload, parse_payload


class OfficeNode(Node):
    """Track attendance and provide absent-student queries."""

    def __init__(self) -> None:
        super().__init__("office_node")
        self.declare_parameter("class_name", "ROS 2 Humble 课堂演示")
        self.declare_parameter("expected_students", ["张三", "李四", "王五", "赵六"])
        self.declare_parameter("allow_unknown_students", False)

        self.class_name = (
            self.get_parameter("class_name").get_parameter_value().string_value
        )
        self.expected_students = list(
            self.get_parameter("expected_students")
            .get_parameter_value()
            .string_array_value
        )
        self.allow_unknown_students = (
            self.get_parameter("allow_unknown_students")
            .get_parameter_value()
            .bool_value
        )
        self.expected_student_set = set(self.expected_students)

        self.current_round = 0
        # 这里只维护“当前轮次”的签到集合，收到新轮次通知后会清空重算。
        self.signed_students: set[str] = set()
        self.classroom = "-"
        self.notice_text = "-"
        self.last_event = "系统已启动，等待老师发布签到通知。"

        self.notice_subscription = self.create_subscription(
            String, "/class_notice", self.notice_callback, 10
        )
        self.attendance_subscription = self.create_subscription(
            String, "/attendance", self.attendance_callback, 10
        )
        self.status_publisher = self.create_publisher(
            String, "/attendance_status", 10
        )
        self.query_service = self.create_service(
            Trigger,
            "/query_absent_students",
            self.handle_query_absent_students,
        )
        self.summary_service = self.create_service(
            Trigger,
            "/query_attendance_summary",
            self.handle_query_attendance_summary,
        )
        self.reset_service = self.create_service(
            Trigger, "/reset_attendance", self.handle_reset_attendance
        )

        self.get_logger().info(
            f"OfficeNode 已启动: class_name={self.class_name}, "
            "expected_students="
            f"{self.expected_students}, "
            f"allow_unknown_students={self.allow_unknown_students}"
        )
        self.publish_status()

    def notice_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
        except (KeyError, ValueError):
            self.get_logger().warning(f"收到无法解析的课堂通知，已忽略: {msg.data}")
            return

        self.class_name = payload.get("class_name", self.class_name)
        self.classroom = payload.get("classroom", self.classroom)
        self.notice_text = payload.get("notice", self.notice_text)

        if round_id > self.current_round:
            self.current_round = round_id
            self.signed_students.clear()
            self.last_event = f"第 {round_id} 轮签到已开始。"
            self.get_logger().info(
                "OfficeNode 开始统计第 "
                f"{round_id} 轮签到，应签到学生: {self.expected_students}"
            )
        else:
            self.last_event = f"收到第 {round_id} 轮重复通知，保持当前统计状态。"
            self.get_logger().info(
                f"OfficeNode 收到第 {round_id} 轮重复通知，保持当前统计状态。"
            )
        self.publish_status()

    def attendance_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
            student_name = payload["student_name"]
        except (KeyError, ValueError):
            self.get_logger().warning(f"收到无法解析的签到消息，已忽略: {msg.data}")
            return

        if round_id != self.current_round:
            self.last_event = (
                f"忽略第 {round_id} 轮签到，当前统计轮次为第 {self.current_round} 轮。"
            )
            self.get_logger().warning(
                "收到第 "
                f"{round_id} 轮签到，但当前统计轮次为第 "
                f"{self.current_round} 轮，已忽略。"
            )
            self.publish_status()
            return

        if (
            student_name not in self.expected_student_set
            and not self.allow_unknown_students
        ):
            self.last_event = f"名单外学生 {student_name} 的签到已被忽略。"
            self.get_logger().warning(
                f"收到名单外学生 {student_name} 的签到消息，"
                "已记录为异常输入并忽略。"
            )
            self.publish_status()
            return

        if (
            student_name not in self.expected_student_set
            and self.allow_unknown_students
        ):
            self.expected_students.append(student_name)
            self.expected_student_set.add(student_name)

        if student_name in self.signed_students:
            self.last_event = f"{student_name} 在第 {round_id} 轮重复签到，已忽略。"
            self.get_logger().info(
                f"{student_name} 在第 {round_id} 轮重复签到，已忽略。"
            )
            self.publish_status()
            return

        self.signed_students.add(student_name)
        absent_students = self.get_absent_students()
        self.last_event = f"{student_name} 已完成第 {round_id} 轮签到。"
        self.get_logger().info(
            f"第 {round_id} 轮签到更新: {student_name} 已签到。"
            f" 当前已签到 "
            f"{len(self.signed_students)}/{len(self.expected_students)}，"
            f" 未签到: {absent_students if absent_students else '无'}"
        )
        self.publish_status()

    def get_absent_students(self) -> list[str]:
        # 保持 expected_students 的原始顺序，返回结果更适合课堂展示。
        return [
            name for name in self.expected_students
            if name not in self.signed_students
        ]

    def handle_query_absent_students(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        del request
        response.success = True

        absent_students = self.get_absent_students()
        if self.current_round == 0:
            response.message = (
                "当前尚未开始签到。待签到学生: " + ", ".join(self.expected_students)
            )
        elif absent_students:
            response.message = "未签到: " + ", ".join(absent_students)
        else:
            response.message = "全部签到"

        self.get_logger().info(
            f"服务 /query_absent_students 被调用，返回结果: {response.message}"
        )
        return response

    def handle_query_attendance_summary(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        del request
        response.success = True
        absent_students = self.get_absent_students()
        signed_students = self.expected_students_signed_in_order()
        response.message = (
            f"round={self.current_round}; "
            f"signed={len(self.signed_students)}/"
            f"{len(self.expected_students)}; "
            "signed_students="
            f"{', '.join(signed_students) if signed_students else '无'}; "
            "absent_students="
            f"{', '.join(absent_students) if absent_students else '无'}"
        )
        self.get_logger().info(
            f"服务 /query_attendance_summary 被调用，返回结果: {response.message}"
        )
        return response

    def handle_reset_attendance(
        self, request: Trigger.Request, response: Trigger.Response
    ) -> Trigger.Response:
        del request
        self.current_round = 0
        self.signed_students.clear()
        self.notice_text = "-"
        self.last_event = "签到状态已重置，等待下一轮通知。"
        self.publish_status()
        response.success = True
        response.message = "签到状态已重置"
        self.get_logger().info(
            f"服务 /reset_attendance 被调用，返回结果: {response.message}"
        )
        return response

    def expected_students_signed_in_order(self) -> list[str]:
        return [
            name for name in self.expected_students
            if name in self.signed_students
        ]

    def publish_status(self) -> None:
        absent_students = self.get_absent_students()
        signed_students = self.expected_students_signed_in_order()
        state = "idle" if self.current_round == 0 else "running"

        msg = String()
        msg.data = build_payload(
            round=self.current_round,
            state=state,
            class_name=self.class_name,
            classroom=self.classroom,
            notice=self.notice_text,
            signed_count=len(signed_students),
            expected_count=len(self.expected_students),
            signed_students=signed_students or "-",
            absent_students=absent_students or "-",
            last_event=self.last_event,
        )
        self.status_publisher.publish(msg)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = OfficeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
