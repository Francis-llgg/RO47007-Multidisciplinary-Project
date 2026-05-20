from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    map_name = LaunchConfiguration("map_name")

    slam_params_file = PathJoinSubstitution([
        FindPackageShare("mdp_mapping"),
        "config",
        "slam_toolbox.yaml",
    ])

    map_save_dir = PathJoinSubstitution([
        FindPackageShare("mdp_mapping"),
        "maps",
    ])

    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("slam_toolbox"),
                "launch",
                "online_async_launch.py",
            ])
        ]),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "slam_params_file": slam_params_file,
        }.items(),
    )

    mapping_manager_node = Node(
        package="mdp_mapping",
        executable="mapping_manager_node",
        name="mapping_manager_node",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "map_save_dir": map_save_dir,
                "map_name": map_name,
                "scan_topic": "/scan",
                "odom_topic": "/odom",
                "map_topic": "/map",
            }
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation time if running in Gazebo.",
        ),

        DeclareLaunchArgument(
            "map_name",
            default_value="greenhouse_map",
            description="Base name of the saved map.",
        ),

        slam_toolbox_launch,
        mapping_manager_node,
    ])