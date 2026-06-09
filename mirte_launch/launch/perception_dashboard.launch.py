#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    network = LaunchConfiguration('network')
    confidence = LaunchConfiguration('confidence')

    return LaunchDescription([
        DeclareLaunchArgument(
            'network',
            default_value='ethernet',
            description='Network mode used by the dashboard robot launch'
        ),

        DeclareLaunchArgument(
            'confidence',
            default_value='0.50',
            description='YOLO confidence threshold for the flower detector'
        ),

        # LED strip battery monitor
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('led_strip'),
                    'launch',
                    'battery_monitor.launch.py'
                ])
            ])
        ),

        # Localization using SLAM Toolbox
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('mdp_localization'),
                    'launch',
                    'localization_slamtoolbox.launch.py'
                ])
            ])
        ),

        # Perception dashboard bridge
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('perception_dashboard_bridge'),
                    'launch',
                    'dashboard_bridge.launch.py'
                ])
            ])
        ),

        # Dashboard robot launch
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('dashboard'),
                    'launch',
                    'robot.launch.py'
                ])
            ]),
            launch_arguments={
                'network': network,
            }.items()
        ),

        # Full perception pipeline
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('flower_detector'),
                    'launch',
                    'mirte_full_perception.launch.py'
                ])
            ]),
            launch_arguments={
                'confidence': confidence,
            }.items()
        ),
    ])