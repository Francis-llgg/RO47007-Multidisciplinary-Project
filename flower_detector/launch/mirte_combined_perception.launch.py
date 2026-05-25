#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    model_path = LaunchConfiguration('model_path')
    confidence = LaunchConfiguration('confidence')

    return LaunchDescription([
        DeclareLaunchArgument(
            'model_path',
            default_value=PathJoinSubstitution([FindPackageShare('flower_detector'),'models','best.pt']),
            description='Path to the YOLO flower detector weights'
        ),

        DeclareLaunchArgument(
            'confidence',
            default_value='0.50',
            description='YOLO confidence threshold'
        ),

        # AprilTag detector for MIRTE gripper camera.
        # Subscribes to /gripper_camera/image_raw
        # Publishes /gripper_camera/tags and /gripper_camera/image_tags
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('apriltag_detector'),
                    'launch',
                    'detect.launch.py'
                ])
            ]),
            launch_arguments={
                'camera': '/gripper_camera',
                'image': 'image_raw',
                'type': 'umich',
                'tag_family': 'tf36h11',
            }.items()
        ),

        # YOLO flower detector for MIRTE gripper camera.
        # Subscribes to /gripper_camera/image_raw
        # Publishes /flower_detector/detections and /flower_detector/image_annotated
        Node(
            package='flower_detector',
            executable='yolo_flower_detector',
            name='yolo_flower_detector',
            output='screen',
            parameters=[{
                'model_path': model_path,
                'image_topic': '/gripper_camera/image_raw',
                'confidence': confidence,
            }],
        ),

        # Combined visualizer.
        # Subscribes to /gripper_camera/image_raw, /flower_detector/detections, /gripper_camera/tags
        # Publishes /perception/image_combined
        Node(
            package='flower_detector',
            executable='combined_visualizer',
            name='combined_visualizer',
            output='screen',
            parameters=[{
                'image_topic': '/gripper_camera/image_raw',
                'flower_topic': '/flower_detector/detections',
                'tag_topic': '/gripper_camera/tags',
                'output_topic': '/perception/image_combined',
            }],
        ),
    ])
