import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():

    # Path to React dashboard
    dashboard_path = os.path.join(
        os.getenv("HOME"),
        "ros2_ws/src/mdp_mirte_master/dashboard/mirte_dashboard"
    )

    # Start React (Vite dev server)
    dashboard = ExecuteProcess(
        cmd=[
            "bash",
            "-c",
            f"cd {dashboard_path} && npm run dev -- --host"
        ],
        output="screen",
        additional_env={
            "VITE_ROS_URL": 'ws://localhost:9090'
        }
    )

    # rosbridge
    rosbridge = Node(
        package="rosbridge_server",
        executable="rosbridge_websocket",
        output="screen"
    )

    return LaunchDescription([
        rosbridge,
        dashboard
    ])
