from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    slam_params_file = LaunchConfiguration("slam_params_file")

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
                [FindPackageShare("slam_toolbox"), "launch", "localization_launch.py"]
            )
        ]),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "slam_params_file": slam_params_file,
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
                "slam_params_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("mdp_localization"),
                        "config",
                        "slam_toolbox_localization.yaml",
                    ]
                ),
                description="Slam toolbox localization parameters file.",
            ),
            scan_filter_node,
            localization_launch,
        ]
    )