import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # Get package share directory (portable way)
    package_share = get_package_share_directory("dashboard")

    # Path to React dashboard
    dashboard_path = os.path.join(
        package_share,
        "mirte_dashboard",
        "mirte_dashboard"
    )

    # Start React
    network = LaunchConfiguration('network').perform(context)
    WIFI_URL = 'ws://192.168.43.204:9090'
    ETHERNET_URL = 'ws://10.42.0.142:9090'
    ros_url = ETHERNET_URL if network == "ethernet" else WIFI_URL


    dashboard = ExecuteProcess(
        cmd=[
            "bash",
            "-c",
            f"cd {dashboard_path} && npm run dev -- --host"
        ],
        output="screen",
        additional_env={
            "VITE_ROS_URL": ros_url,
            "VITE_CMD_TOPIC": '/mirte_base_controller/cmd_vel'
        }
    )

    return LaunchDescription([
        dashboard
    ])
