from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger

from .message_utils import parse_payload


class OfficeNode(Node):
    """Track attendance and provide absent-student queries."""

    def __init__(self) -> None:
        super().__init__("office_node")
        self.declare_parameter("class_name", "ROS 2 Humble 课堂演示")
        self.declare_parameter("expected_students", ["张三", "李四", "王五", "赵六"])

        self.class_name = self.get_parameter("class_name").get_parameter_value().string_value
        self.expected_students = list(
            self.get_parameter("expected_students").get_parameter_value().string_array_value
        )
        self.expected_student_set = set(self.expected_students)

        self.current_round = 0
        # 这里只维护“当前轮次”的签到集合，收到新轮次通知后会清空重算。
        self.signed_students: set[str] = set()

        self.notice_subscription = self.create_subscription(
            String, "/class_notice", self.notice_callback, 10
        )
        self.attendance_subscription = self.create_subscription(
            String, "/attendance", self.attendance_callback, 10
        )
        self.query_service = self.create_service(
            Trigger, "/query_absent_students", self.handle_query_absent_students
        )

        self.get_logger().info(
            f"OfficeNode 已启动: class_name={self.class_name}, "
            f"expected_students={self.expected_students}"
        )

    def notice_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
        except (KeyError, ValueError):
            self.get_logger().warning(f"收到无法解析的课堂通知，已忽略: {msg.data}")
            return

        if round_id > self.current_round:
            self.current_round = round_id
            self.signed_students.clear()
            self.get_logger().info(
                f"OfficeNode 开始统计第 {round_id} 轮签到，应签到学生: {self.expected_students}"
            )
        else:
            self.get_logger().info(
                f"OfficeNode 收到第 {round_id} 轮重复通知，保持当前统计状态。"
            )

    def attendance_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
            student_name = payload["student_name"]
        except (KeyError, ValueError):
            self.get_logger().warning(f"收到无法解析的签到消息，已忽略: {msg.data}")
            return

        if round_id != self.current_round:
            self.get_logger().warning(
                f"收到第 {round_id} 轮签到，但当前统计轮次为第 {self.current_round} 轮，已忽略。"
            )
            return

        if student_name not in self.expected_student_set:
            self.get_logger().warning(
                f"收到名单外学生 {student_name} 的签到消息，已记录为异常输入并忽略。"
            )
            return

        if student_name in self.signed_students:
            self.get_logger().info(
                f"{student_name} 在第 {round_id} 轮重复签到，已忽略。"
            )
            return

        self.signed_students.add(student_name)
        absent_students = self.get_absent_students()
        self.get_logger().info(
            f"第 {round_id} 轮签到更新: {student_name} 已签到。"
            f" 当前已签到 {len(self.signed_students)}/{len(self.expected_students)}，"
            f" 未签到: {absent_students if absent_students else '无'}"
        )

    def get_absent_students(self) -> list[str]:
        # 保持 expected_students 的原始顺序，返回结果更适合课堂展示。
        return [name for name in self.expected_students if name not in self.signed_students]

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
