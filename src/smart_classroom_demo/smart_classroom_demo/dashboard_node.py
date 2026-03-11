from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .message_utils import parse_payload


class DashboardNode(Node):
    """Render a compact classroom status board for demos."""

    def __init__(self) -> None:
        super().__init__("dashboard_node")
        self.declare_parameter("expected_students", ["张三", "李四", "王五", "赵六"])

        self.expected_students = list(
            self.get_parameter("expected_students").get_parameter_value().string_array_value
        )
        # 这个节点不参与业务决策，只把当前课堂状态汇总成一个终端面板。
        self.current_round = 0
        self.class_name = "未开始"
        self.classroom = "-"
        self.notice_text = "-"
        self.signed_students: set[str] = set()
        self.last_event = "系统已启动，等待老师发布课堂通知。"

        self.create_subscription(String, "/class_notice", self.notice_callback, 10)
        self.create_subscription(String, "/attendance", self.attendance_callback, 10)

        self.render_board()

    def notice_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
        except (KeyError, ValueError):
            self.last_event = f"收到无法解析的课堂通知: {msg.data}"
            self.render_board()
            return

        self.current_round = round_id
        self.class_name = payload.get("class_name", "未知课程")
        self.classroom = payload.get("classroom", "未知教室")
        self.notice_text = payload.get("notice", "")
        # 收到新一轮通知后，面板上的签到人数也要重新从 0 开始统计。
        self.signed_students.clear()
        self.last_event = f"老师已发布第 {round_id} 轮通知。"
        self.render_board()

    def attendance_callback(self, msg: String) -> None:
        payload = parse_payload(msg.data)
        try:
            round_id = int(payload["round"])
            student_name = payload["student_name"]
        except (KeyError, ValueError):
            self.last_event = f"收到无法解析的签到消息: {msg.data}"
            self.render_board()
            return

        if round_id != self.current_round:
            self.last_event = (
                f"忽略第 {round_id} 轮签到，当前展示轮次为第 {self.current_round} 轮。"
            )
            self.render_board()
            return

        self.signed_students.add(student_name)
        self.last_event = f"{student_name} 已完成第 {round_id} 轮签到。"
        self.render_board()

    def render_board(self) -> None:
        # 这里不用 set 直接打印，是为了保持 expected_students 里的展示顺序稳定。
        signed = [name for name in self.expected_students if name in self.signed_students]
        absent = [name for name in self.expected_students if name not in self.signed_students]

        lines = [
            "",
            "=" * 54,
            "智能课堂通知与签到系统",
            "-" * 54,
            f"当前轮次: 第 {self.current_round} 轮",
            f"课程名称: {self.class_name}",
            f"教室信息: {self.classroom}",
            f"通知内容: {self.notice_text}",
            "-" * 54,
            f"已签到 ({len(signed)}/{len(self.expected_students)}): "
            f"{', '.join(signed) if signed else '暂无'}",
            f"未签到 ({len(absent)}/{len(self.expected_students)}): "
            f"{', '.join(absent) if absent else '无'}",
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
