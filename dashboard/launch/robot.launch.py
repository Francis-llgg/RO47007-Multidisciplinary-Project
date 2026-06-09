import os

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    package_share = get_package_share_directory("dashboard")

    dashboard_path = os.path.join(
        package_share,
        "mirte_dashboard",
        "mirte_dashboard"
    )

    network = LaunchConfiguration("network", default="wifi")

    WIFI_URL = "ws://192.168.43.204:9090"
    ##TODO; update this to get actual ip address on setup
    ETHERNET_URL = "ws://192.168.45.1:9090"

    ros_url = PythonExpression([
        "'",
        ETHERNET_URL,
        "' if '",
        network,
        "' == 'ethernet' else '",
        WIFI_URL,
        "'"
    ])

    dashboard = ExecuteProcess(
        cmd=[
            "bash",
            "-c",
            f"cd {dashboard_path} && npm run dev -- --host"
        ],
        output="screen",
        additional_env={
            "VITE_ROS_URL": ros_url,
            "VITE_CMD_TOPIC": "/mirte_base_controller/cmd_vel"
        }
    )

    return LaunchDescription([
        dashboard
    ])