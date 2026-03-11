from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .message_utils import parse_csv_field, parse_payload


class DashboardNode(Node):
    """Render a compact classroom status board for demos."""

    def __init__(self) -> None:
        super().__init__("dashboard_node")
        self.declare_parameter("expected_students", ["张三", "李四", "王五", "赵六"])
        self.declare_parameter("refresh_on_event_only", True)

        self.expected_students = list(
            self.get_parameter("expected_students")
            .get_parameter_value()
            .string_array_value
        )
        self.refresh_on_event_only = (
            self.get_parameter("refresh_on_event_only")
            .get_parameter_value()
            .bool_value
        )
        # 这个节点不参与业务决策，只消费 office_node 的状态 topic 做展示。
        self.current_round = 0
        self.state = "idle"
        self.class_name = "未开始"
        self.classroom = "-"
        self.notice_text = "-"
        self.signed_students: list[str] = []
        self.absent_students = list(self.expected_students)
        self.last_event = "系统已启动，等待老师发布课堂通知。"

        self.create_subscription(
            String, "/attendance_status", self.status_callback, 10
        )

        self.render_board()

    def status_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
        except (KeyError, ValueError):
            self.last_event = f"收到无法解析的状态消息: {msg.data}"
            self.render_board()
            return

        self.current_round = round_id
        self.state = payload.get("state", "idle")
        self.class_name = payload.get("class_name", "未知课程")
        self.classroom = payload.get("classroom", "未知教室")
        self.notice_text = payload.get("notice", "")
        self.signed_students = parse_csv_field(
            payload.get("signed_students", "")
        )
        absent_field = payload.get("absent_students", "")
        self.absent_students = parse_csv_field(absent_field)
        self.last_event = payload.get("last_event", self.last_event)
        if not self.refresh_on_event_only or self.last_event:
            self.render_board()

    def render_board(self) -> None:
        lines = [
            "",
            "=" * 54,
            "智能课堂通知与签到系统",
            "-" * 54,
            f"当前轮次: 第 {self.current_round} 轮",
            f"系统状态: {self.state}",
            f"课程名称: {self.class_name}",
            f"教室信息: {self.classroom}",
            f"通知内容: {self.notice_text}",
            "-" * 54,
            (
                f"已签到 ({len(self.signed_students)}/"
                f"{len(self.expected_students)}): "
            ) + (
                ', '.join(self.signed_students)
                if self.signed_students else '暂无'
            ),
            (
                f"未签到 ({len(self.absent_students)}/"
                f"{len(self.expected_students)}): "
            ) + (
                ', '.join(self.absent_students)
                if self.absent_students else '无'
            ),
            "-" * 54,
            f"最新事件: {self.last_event}",
            "=" * 54,
        ]
        self.get_logger().info("\n".join(lines))


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = DashboardNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
