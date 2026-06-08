from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import (
    AnyLaunchDescriptionSource,
    PythonLaunchDescriptionSource,
)


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    world = LaunchConfiguration("world")
    map_name = LaunchConfiguration("map_name")
    map_save_dir = LaunchConfiguration("map_save_dir")

    nav2_params_file = PathJoinSubstitution([
        FindPackageShare("mdp_navigation"),
        "config",
        "nav2_params.yaml",
    ])

    rviz_config_file = PathJoinSubstitution([
        FindPackageShare("nav2_bringup"),
        "rviz",
        "nav2_default_view.rviz",
    ])

    slam_params_file = PathJoinSubstitution([
        FindPackageShare("mdp_mapping"),
        "config",
        "slam_toolbox.yaml",
    ])

    gazebo_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("mirte_gazebo"),
                "launch",
                "gazebo_mirte_master_empty.launch.xml",
            ])
        ),
        launch_arguments={
            "world": world,
        }.items(),
    )

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

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("nav2_bringup"),
                "launch",
                "navigation_launch.py",
            ])
        ]),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "autostart": "true",
            "params_file": nav2_params_file,
        }.items(),
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
        parameters=[
            {
                "use_sim_time": use_sim_time,
            }
        ],
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
                # Subscribe to filtered scan published by filter node
                "scan_topic": "/scan_filtered",
                "odom_topic": "/odom",
                "map_topic": "/map",
            }
        ],
    )

    scan_filter_node = Node(
        package="mdp_mapping",
        executable="scan_self_filter_node",
        name="scan_self_filter_node",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "input_scan_topic": "/scan",
                "output_scan_topic": "/scan_filtered",
                "self_clear_radius": 0.15,
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
            "world",
            default_value="/home/zheng/ros2_ws/src/mdp_mirte_master/greenhouse_simulation/worlds/greenhouse.world",
            description="Full path to the Gazebo world file.",
        ),

        DeclareLaunchArgument(
            "map_name",
            default_value="greenhouse_map",
            description="Base name of the saved map.",
        ),

        DeclareLaunchArgument(
            "map_save_dir",
            default_value="/home/zheng/ros2_ws/src/mdp_mirte_master/maps",
            description="Directory where maps and posegraphs are saved.",
        ),

        gazebo_launch,
        slam_toolbox_launch,
        scan_filter_node,
        mapping_manager_node,
        nav2_launch,
        rviz_node,
    ])
 