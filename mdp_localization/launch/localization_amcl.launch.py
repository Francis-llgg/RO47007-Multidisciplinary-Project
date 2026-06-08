from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    map_file = LaunchConfiguration("map")
    params_file = LaunchConfiguration("params_file")

    scan_filter_node = Node(
        package="mdp_mapping",
        executable="scan_self_filter_node",
        name="scan_self_filter_node",
        output="screen",
        parameters=[
            {
                "input_scan_topic": "/scan",
                "output_scan_topic": "/scan_filtered",
                "self_clear_radius": 0.15,
            }
        ],
    )

    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution(
                [FindPackageShare("nav2_bringup"), "launch", "localization_launch.py"]
            )
        ]),
        launch_arguments={
            "map": map_file,
            "use_sim_time": use_sim_time,
            "params_file": params_file,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use simulation time.",
            ),
            DeclareLaunchArgument(
                "map",
                default_value="/home/zheng/ros2_ws/src/mdp_mirte_master/maps/greenhouse_map.yaml",
                description="Full path to the map yaml file.",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("mdp_localization"), "config", "nav2_params.yaml"]
                ),
                description="Nav2 parameters file.",
            ),
            scan_filter_node,
            localization_launch,
        ]
    )