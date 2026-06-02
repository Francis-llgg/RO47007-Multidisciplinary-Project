from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch_ros.actions import SetRemap
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution

from ament_index_python.packages import get_package_share_directory
import os

map_file = os.path.join(
    get_package_share_directory("mirte_launch"),
    "maps",
    "map.yaml"
)

params_file = os.path.join(
    get_package_share_directory("mirte_launch"),
    "config",
    "nav2_params.yaml"
)

use_sim_time = "true"
autostart = "true"

# Navigation launch
navigation_launch = GroupAction(
        actions=[
            SetRemap(src='/cmd_vel', dst='/mirte_base_controller/cmd_vel_unstamped'),
            SetRemap(src='cmd_vel', dst='/mirte_base_controller/cmd_vel_unstamped'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(PathJoinSubstitution([
                    FindPackageShare("nav2_bringup"), "launch", "bringup_launch.py"
                ])),
                launch_arguments={
                    "map": map_file,
                    "params_file": params_file,
                    "use_sim_time": use_sim_time,
                    "autostart": autostart,
                }.items()
            )
        ]
    )
def generate_launch_description():
    return LaunchDescription([ 
        navigation_launch
	])