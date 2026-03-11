from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .message_utils import build_payload, parse_payload


class StudentNode(Node):
    """Subscribe to class notices and publish attendance once per round."""

    def __init__(self) -> None:
        super().__init__("student_node")
        self.declare_parameter("student_name", "张三")
        self.declare_parameter("auto_signin_delay", 1.0)
        self.declare_parameter("auto_signin_enabled", True)

        self.student_name = (
            self.get_parameter("student_name")
            .get_parameter_value()
            .string_value
        )
        self.auto_signin_delay = (
            self.get_parameter("auto_signin_delay")
            .get_parameter_value()
            .double_value
        )
        self.auto_signin_enabled = (
            self.get_parameter("auto_signin_enabled")
            .get_parameter_value()
            .bool_value
        )

        self.notice_subscription = self.create_subscription(
            String, "/class_notice", self.notice_callback, 10
        )
        self.attendance_publisher = self.create_publisher(
            String, "/attendance", 10
        )

        # last_signed_round 防止同一轮重复签到；
        # pending_round / pending_timer 表示“已经收到通知，但还在等待延迟签到”。
        self.last_signed_round = 0
        self.pending_round = None
        self.pending_timer = None

        self.get_logger().info(
            f"StudentNode 已启动: student_name={self.student_name}, "
            f"auto_signin_delay={self.auto_signin_delay:.1f}s, "
            f"auto_signin_enabled={self.auto_signin_enabled}"
        )

    def notice_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
        except (KeyError, ValueError):
            self.get_logger().warning(f"收到无法解析的课堂通知，已忽略: {msg.data}")
            return

        class_name = payload.get("class_name", "未知课程")
        classroom = payload.get("classroom", "未知教室")
        notice = payload.get("notice", "")

        if round_id <= self.last_signed_round:
            self.get_logger().info(
                f"{self.student_name} 收到第 {round_id} 轮重复通知，已忽略。"
            )
            return

        if self.pending_round == round_id:
            self.get_logger().info(
                f"{self.student_name} 已在准备第 {round_id} 轮签到，不重复创建定时器。"
            )
            return

        if self.pending_timer is not None:
            # 如果老师开始了新一轮签到，取消上一轮尚未触发的定时器。
            self.pending_timer.cancel()
            self.pending_timer = None

        self.pending_round = round_id
        self.get_logger().info(
            f"{self.student_name} 收到课堂通知: 第 {round_id} 轮, "
            f"课程={class_name}, 教室={classroom}, 内容={notice}"
        )
        if not self.auto_signin_enabled:
            self.get_logger().info(
                f"{self.student_name} 当前关闭自动签到，仅接收通知不发送签到。"
            )
            return
        self.get_logger().info(
            f"{self.student_name} 将在 {self.auto_signin_delay:.1f} 秒后自动签到。"
        )
        self.pending_timer = self.create_timer(
            self.auto_signin_delay, self.publish_attendance
        )

    def publish_attendance(self) -> None:
        if self.pending_round is None:
            return

        if self.pending_timer is not None:
            self.pending_timer.cancel()
            self.pending_timer = None

        round_id = self.pending_round
        if round_id <= self.last_signed_round:
            self.get_logger().info(
                f"{self.student_name} 对第 {round_id} 轮已完成签到，本次发送取消。"
            )
            self.pending_round = None
            return

        msg = String()
        # 办公节点依靠 round + student_name 识别是哪位同学在哪一轮签到。
        msg.data = build_payload(
            round=round_id,
            student_name=self.student_name,
            status="已签到",
        )
        self.attendance_publisher.publish(msg)
        self.last_signed_round = round_id
        self.pending_round = None

        self.get_logger().info(f"{self.student_name} 已完成第 {round_id} 轮签到。")


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = StudentNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
