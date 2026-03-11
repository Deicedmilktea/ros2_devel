from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    default_config_file = PathJoinSubstitution(
        [FindPackageShare("smart_classroom_demo"), "config", "classroom_demo.yaml"]
    )
    config_file = LaunchConfiguration("config_file")
    auto_start = LaunchConfiguration("auto_start")
    enable_dashboard = LaunchConfiguration("enable_dashboard")
    enable_wangwu = LaunchConfiguration("enable_wangwu")

    launch_arguments = [
        DeclareLaunchArgument(
            "config_file",
            default_value=default_config_file,
            description="Path to the ROS2 parameter YAML file.",
        ),
        DeclareLaunchArgument(
            "auto_start",
            default_value="true",
            description="Whether teacher_node should publish the first attendance round on startup.",
        ),
        DeclareLaunchArgument(
            "enable_dashboard",
            default_value="true",
            description="Whether to launch dashboard_node for terminal visualization.",
        ),
        DeclareLaunchArgument(
            "enable_wangwu",
            default_value="true",
            description="Whether to launch the Wangwu student node.",
        ),
    ]

    teacher_node = Node(
        package="smart_classroom_demo",
        executable="teacher_node",
        name="teacher_node",
        output="log",
        parameters=[config_file, {"auto_start_enabled": auto_start}],
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
        condition=IfCondition(enable_dashboard),
    )

    student_nodes = [
        Node(
            package="smart_classroom_demo",
            executable="student_node",
            name="student_zhangsan",
            output="log",
            parameters=[config_file],
        ),
        Node(
            package="smart_classroom_demo",
            executable="student_node",
            name="student_lisi",
            output="log",
            parameters=[config_file],
        ),
        Node(
            package="smart_classroom_demo",
            executable="student_node",
            name="student_wangwu",
            output="log",
            parameters=[config_file],
            condition=IfCondition(enable_wangwu),
        ),
    ]

    return LaunchDescription(
        [
            *launch_arguments,
            teacher_node,
            office_node,
            dashboard_node,
            *student_nodes,
        ]
    )
