#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, EnvironmentVariable, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    snapshot_dir = LaunchConfiguration('snapshot_dir')
    base_url = LaunchConfiguration('base_url')

    default_snapshot_dir = PathJoinSubstitution([
        EnvironmentVariable('HOME'),
        'ros2_ws',
        'perception_snapshots'
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            'snapshot_dir',
            default_value=default_snapshot_dir,
            description='Directory containing saved perception PNG and JSON snapshots'
        ),

        DeclareLaunchArgument(
            'base_url',
            default_value='http://localhost:8088',
            description='Base URL used by dashboard to access saved snapshots'
        ),

        # HTTP server for saved PNG + JSON files.
        # Makes snapshots accessible through:
        #   http://localhost:8088/perception_snapshot_....png
        ExecuteProcess(
            cmd=[
                'bash',
                '-lc',
                'mkdir -p "$HOME/ros2_ws/perception_snapshots" && '
                'cd "$HOME/ros2_ws/perception_snapshots" && '
                'python3 -m http.server 8088'
            ],
            output='screen'
        ),

        # Publishes latest saved PNG + JSON metadata on /latest_observation.
        Node(
            package='perception_dashboard_bridge',
            executable='latest_observation_publisher',
            name='latest_observation_publisher',
            output='screen',
            parameters=[{
                'snapshot_dir': snapshot_dir,
                'publish_topic': '/latest_observation',
                'publish_rate_hz': 1.0,
                'base_url': base_url,
            }],
        ),
    ])
