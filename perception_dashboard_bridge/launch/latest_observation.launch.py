#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch_ros.actions import Node

snapshot_dir = os.path.join(
    os.path.expanduser('~/ros2_ws'),
    'perception_snapshots'
)


def generate_launch_description():
    print("snapshot_dir:", snapshot_dir, type(snapshot_dir))
    return LaunchDescription([
      ExecuteProcess(
            cmd=[
                'python3',
                '-m',
                'http.server',
                '8088',
                '--directory',
                snapshot_dir,
            ],
            output='screen',
        ),

        Node(
            package='perception_dashboard_bridge',
            executable='latest_observation_publisher',
            name='latest_observation_publisher',
            output='screen',
            parameters=[{
                'snapshot_dir': snapshot_dir,
                'publish_topic': '/latest_observation',
                'publish_rate_hz': 1.0,
                'base_url': 'http://localhost:8088',
            }],
        ),
    ])
