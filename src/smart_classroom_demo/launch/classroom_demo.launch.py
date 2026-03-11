from launch import LaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    config_file = PathJoinSubstitution(
        [FindPackageShare("smart_classroom_demo"), "config", "classroom_demo.yaml"]
    )

    teacher_node = Node(
        package="smart_classroom_demo",
        executable="teacher_node",
        name="teacher_node",
        output="log",
        parameters=[config_file],
    )

    office_node = Node(
        package="smart_classroom_demo",
        executable="office_node",
        name="office_node",
        output="log",
        parameters=[config_file],
    )

    dashboard_node = Node(
        package="smart_classroom_demo",
        executable="dashboard_node",
        name="dashboard_node",
        output="screen",
        emulate_tty=True,
        parameters=[config_file],
    )

    student_nodes = [
        Node(
            package="smart_classroom_demo",
            executable="student_node",
            name="student_zhangsan",
            output="log",
            parameters=[
                {"student_name": "张三", "auto_signin_delay": 5.0},
            ],
        ),
        Node(
            package="smart_classroom_demo",
            executable="student_node",
            name="student_lisi",
            output="log",
            parameters=[
                {"student_name": "李四", "auto_signin_delay": 10.0},
            ],
        ),
        Node(
            package="smart_classroom_demo",
            executable="student_node",
            name="student_wangwu",
            output="log",
            parameters=[
                {"student_name": "王五", "auto_signin_delay": 15.0},
            ],
        ),
    ]

    return LaunchDescription([teacher_node, office_node, dashboard_node, *student_nodes])
