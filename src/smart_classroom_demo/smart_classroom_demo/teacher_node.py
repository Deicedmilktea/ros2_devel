from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .message_utils import build_payload


class TeacherNode(Node):
    """Publish class notices and start attendance rounds."""

    def __init__(self) -> None:
        super().__init__("teacher_node")
        self.declare_parameter("class_name", "ROS 2 Humble 课堂演示")
        self.declare_parameter("classroom", "A101")
        self.declare_parameter("notice_text", "开始上课，请同学们完成签到")
        self.declare_parameter("publish_on_start", True)
        self.declare_parameter("publish_period_sec", 0.0)

        self.class_name = self.get_parameter("class_name").get_parameter_value().string_value
        self.classroom = self.get_parameter("classroom").get_parameter_value().string_value
        self.notice_text = self.get_parameter("notice_text").get_parameter_value().string_value
        self.publish_on_start = (
            self.get_parameter("publish_on_start").get_parameter_value().bool_value
        )
        self.publish_period_sec = (
            self.get_parameter("publish_period_sec").get_parameter_value().double_value
        )

        self.notice_publisher = self.create_publisher(String, "/class_notice", 10)
        # round_id 用来标记“第几轮签到”，学生和教学办都依赖它判断是否重复。
        self.round_id = 0
        self.start_timer = None
        self.periodic_timer = None

        self.get_logger().info(
            f"TeacherNode 已启动: class_name={self.class_name}, "
            f"classroom={self.classroom}, publish_on_start={self.publish_on_start}, "
            f"publish_period_sec={self.publish_period_sec:.1f}"
        )

        if self.publish_on_start:
            # 启动后稍等 1 秒再发通知，避免其他节点还没完成订阅。
            self.start_timer = self.create_timer(1.0, self._publish_once_on_start)

        if self.publish_period_sec > 0.0:
            self.periodic_timer = self.create_timer(
                self.publish_period_sec, self.publish_class_notice
            )

    def _publish_once_on_start(self) -> None:
        if self.start_timer is not None:
            self.start_timer.cancel()
        self.publish_class_notice()

    def publish_class_notice(self) -> None:
        self.round_id += 1
        # 仍然使用 String，但把关键字段编码进去，便于演示且不用自定义消息。
        payload = build_payload(
            round=self.round_id,
            class_name=self.class_name,
            classroom=self.classroom,
            notice=self.notice_text,
        )

        msg = String()
        msg.data = payload
        self.notice_publisher.publish(msg)

        self.get_logger().info(
            f"第 {self.round_id} 轮课堂通知已发布: "
            f"[课程: {self.class_name}] [教室: {self.classroom}] [内容: {self.notice_text}]"
        )


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node = TeacherNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
