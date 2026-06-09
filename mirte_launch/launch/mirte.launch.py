from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, GroupAction
from launch_ros.actions import SetRemap, Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
	
from ament_index_python.packages import get_package_share_directory
import os

map_file = os.path.join(
    get_package_share_directory("mirte_launch"),
    "maps",
    "greenhouse_map.yaml"
)

params_file = os.path.join(
    get_package_share_directory("mirte_launch"),
    "config",
    "nav2_params.yaml"
)

sim_world = os.path.join(
	get_package_share_directory("mirte_launch"),
	"worlds",
	"greenhouse.world"
)

rviz_config = os.path.join(
    get_package_share_directory("nav2_bringup"),
    "rviz",
    "nav2_default_view.rviz"
)

use_sim_time = "false"
autostart = "true"

# #Simulation launch (Gazebo)
# simulation_launch = IncludeLaunchDescription(
# 	XMLLaunchDescriptionSource(
#         PathJoinSubstitution([
# 			FindPackageShare("mirte_gazebo"),
# 			"launch",
# 			"gazebo_mirte_master_empty.launch.xml"
# 		])
#     ),
#     launch_arguments={
# 		"world": sim_world
# 	}.items()
# )
#rviz launch
rviz_launch = Node(
      package="rviz2",
      executable= "rviz2",
      name="rviz2",
      arguments=["-d", rviz_config],
      output="screen",
)

# Navigation launch
navigation_launch = GroupAction(
        actions=[
            SetRemap(src='/cmd_vel', dst='/mirte_base_controller/cmd_vel'),
            SetRemap(src='cmd_vel', dst='/mirte_base_controller/cmd_vel'),
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
		navigation_launch,
        rviz_launch,
	])