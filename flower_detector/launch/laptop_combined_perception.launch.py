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
            default_value='/home/nikolaos/mdp_flower_detection/runs/detect/runs/detect/yolo11s_new/weights/best.pt',
            description='Path to the YOLO flower detector weights'
        ),

        DeclareLaunchArgument(
            'confidence',
            default_value='0.50',
            description='YOLO confidence threshold'
        ),

        # Laptop webcam: publishes /camera/image_raw
        Node(
            package='v4l2_camera',
            executable='v4l2_camera_node',
            name='laptop_camera',
            output='screen',
            remappings=[
                ('image_raw', '/camera/image_raw'),
            ],
        ),

        # AprilTag detector: subscribes to /camera/image_raw
        # Publishes /camera/tags and /camera/image_tags
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('apriltag_detector'),
                    'launch',
                    'detect.launch.py'
                ])
            ]),
            launch_arguments={
                'camera': '/camera',
                'image': 'image_raw',
                'type': 'umich',
                'tag_family': 'tf36h11',
            }.items()
        ),

        # YOLO flower detector: subscribes to /camera/image_raw
        # Publishes /flower_detector/detections and /flower_detector/image_annotated
        Node(
            package='flower_detector',
            executable='yolo_flower_detector',
            name='yolo_flower_detector',
            output='screen',
            parameters=[{
                'model_path': model_path,
                'image_topic': '/camera/image_raw',
                'confidence': confidence,
            }],
        ),

        # Combined visualizer: draws flowers + AprilTags on one image
        # Publishes /perception/image_combined
        Node(
            package='flower_detector',
            executable='combined_visualizer',
            name='combined_visualizer',
            output='screen',
            parameters=[{
                'image_topic': '/camera/image_raw',
                'flower_topic': '/flower_detector/detections',
                'tag_topic': '/camera/tags',
                'output_topic': '/perception/image_combined',
            }],
        ),
    ])
