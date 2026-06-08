#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='perception_dashboard_bridge',
            executable='latest_observation_publisher',
            name='latest_observation_publisher',
            output='screen',
            parameters=[{
                'snapshot_dir': '/home/nikolaos/ros2_ws/perception_snapshots',
                'publish_topic': '/latest_observation',
                'publish_rate_hz': 1.0,
                'base_url': 'http://localhost:8088',
            }],
        ),
    ])
