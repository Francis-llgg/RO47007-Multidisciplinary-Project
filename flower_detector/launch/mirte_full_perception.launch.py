# #!/usr/bin/env python3

# from launch import LaunchDescription
# from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
# from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
# from launch.launch_description_sources import PythonLaunchDescriptionSource

# from launch_ros.actions import Node
# from launch_ros.substitutions import FindPackageShare


# def generate_launch_description():
#     model_path = LaunchConfiguration('model_path')
#     confidence = LaunchConfiguration('confidence')

#     return LaunchDescription([
#         DeclareLaunchArgument(
#             'model_path',
#             default_value=PathJoinSubstitution([
#                 FindPackageShare('flower_detector'),
#                 'models',
#                 'best.pt'
#             ]),
#             description='Path to the YOLO flower detector weights'
#         ),

#         DeclareLaunchArgument(
#             'confidence',
#             default_value='0.50',
#             description='YOLO confidence threshold'
#         ),

#         # Greenhouse bridge.
#         # Provides:
#         #   /greenhouse_bridge/get_tag_reading
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource([
#                 PathJoinSubstitution([
#                     FindPackageShare('lupin_greenhouse_bridge'),
#                     'launch',
#                     'greenhouse_bridge.launch.py'
#                 ])
#             ])
#         ),

#         # Decode compressed Wi-Fi image stream into a local raw image topic.
#         # Input:
#         #   /gripper_camera/image_raw/compressed
#         # Output:
#         #   /gripper_camera/image_raw_decoded
#         Node(
#             package='image_transport',
#             executable='republish',
#             name='compressed_to_raw_republisher',
#             output='screen',
#             arguments=['compressed', 'raw'],
#             remappings=[
#                 ('in/compressed', '/gripper_camera/image_raw/compressed'),
#                 ('out', '/gripper_camera/image_raw_decoded'),
#             ],
#         ),

#         # AprilTag detector using decoded raw image.
#         # Input:
#         #   /gripper_camera/image_raw_decoded
#         # Output:
#         #   /gripper_camera/tags
#         #   /gripper_camera/image_tags
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource([
#                 PathJoinSubstitution([
#                     FindPackageShare('apriltag_detector'),
#                     'launch',
#                     'detect.launch.py'
#                 ])
#             ]),
#             launch_arguments={
#                 'camera': '/gripper_camera',
#                 'image': 'image_raw_decoded',
#                 'image_transport': 'raw',
#                 'type': 'umich',
#                 'tag_family': 'tf36h11',
#             }.items()
#         ),

#         # YOLO detector using compressed image directly.
#         # Input:
#         #   /gripper_camera/image_raw/compressed
#         # Output:
#         #   /flower_detector/detections
#         #   /flower_detector/image_annotated
#         Node(
#             package='flower_detector',
#             executable='yolo_flower_detector',
#             name='yolo_flower_detector',
#             output='screen',
#             parameters=[{
#                 'model_path': model_path,
#                 'image_topic': '/gripper_camera/image_raw/compressed',
#                 'confidence': confidence,
#                 'use_compressed': True,
#             }],
#         ),

#         # Combined visualizer.
#         # Input:
#         #   /flower_detector/image_annotated
#         #   /flower_detector/detections
#         #   /gripper_camera/tags
#         # Output:
#         #   /perception/image_combined
#         Node(
#             package='flower_detector',
#             executable='combined_visualizer',
#             name='combined_visualizer',
#             output='screen',
#             parameters=[{
#                 'image_topic': '/flower_detector/image_annotated',
#                 'flower_topic': '/flower_detector/detections',
#                 'tag_topic': '/gripper_camera/tags',
#                 'output_topic': '/perception/image_combined',
#                 'use_compressed': False,
#             }],
#         ),

#         # Greenhouse information reader from detected AprilTag IDs.
#         # Input:
#         #   /gripper_camera/tags
#         # Service call:
#         #   /greenhouse_bridge/get_tag_reading
#         # Output:
#         #   /greenhouse/tag_reading
#         Node(
#             package='flower_detector',
#             executable='greenhouse_tag_reader',
#             name='greenhouse_tag_reader',
#             output='screen',
#             parameters=[{
#                 'tag_topic': '/gripper_camera/tags',
#                 'service_name': '/greenhouse_bridge/get_tag_reading',
#                 'cooldown_sec': 2.0,
#             }],
#         ),

#         # Snapshot saver.
#         # Input:
#         #   /perception/image_combined
#         # Service:
#         #   /save_perception_snapshot
#         # Output:
#         #   saved PNG file path
#         Node(
#             package='flower_detector',
#             executable='perception_snapshot_saver',
#             name='perception_snapshot_saver',
#             output='screen',
#             parameters=[{
#                 'image_topic': '/perception/image_combined',
#                 'snapshot_dir': '/home/nikolaos/ros2_ws/perception_snapshots',
#             }],
#         ),
#     ])


#hard coded 
# #!/usr/bin/env python3

# from launch import LaunchDescription
# from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
# from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
# from launch.launch_description_sources import PythonLaunchDescriptionSource

# from launch_ros.actions import Node
# from launch_ros.substitutions import FindPackageShare


# def generate_launch_description():
#     model_path = LaunchConfiguration('model_path')
#     confidence = LaunchConfiguration('confidence')

#     return LaunchDescription([
#         DeclareLaunchArgument(
#             'model_path',
#             default_value=PathJoinSubstitution([
#                 FindPackageShare('flower_detector'),
#                 'models',
#                 'best.pt'
#             ]),
#             description='Path to the YOLO flower detector weights'
#         ),

#         DeclareLaunchArgument(
#             'confidence',
#             default_value='0.50',
#             description='YOLO confidence threshold'
#         ),

#         # Greenhouse bridge.
#         # Provides:
#         #   /greenhouse_bridge/get_tag_reading
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource([
#                 PathJoinSubstitution([
#                     FindPackageShare('lupin_greenhouse_bridge'),
#                     'launch',
#                     'greenhouse_bridge.launch.py'
#                 ])
#             ])
#         ),

#         # Decode compressed Wi-Fi image stream into a local raw image topic.
#         # Input:
#         #   /gripper_camera/image_raw/compressed
#         # Output:
#         #   /gripper_camera/image_raw_decoded
#         Node(
#             package='image_transport',
#             executable='republish',
#             name='compressed_to_raw_republisher',
#             output='screen',
#             arguments=['compressed', 'raw'],
#             remappings=[
#                 ('in/compressed', '/gripper_camera/image_raw/compressed'),
#                 ('out', '/gripper_camera/image_raw_decoded'),
#             ],
#         ),

#         # AprilTag detector using decoded raw image.
#         # Input:
#         #   /gripper_camera/image_raw_decoded
#         # Output:
#         #   /gripper_camera/tags
#         #   /gripper_camera/image_tags
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource([
#                 PathJoinSubstitution([
#                     FindPackageShare('apriltag_detector'),
#                     'launch',
#                     'detect.launch.py'
#                 ])
#             ]),
#             launch_arguments={
#                 'camera': '/gripper_camera',
#                 'image': 'image_raw_decoded',
#                 'image_transport': 'raw',
#                 'type': 'umich',
#                 'tag_family': 'tf36h11',
#             }.items()
#         ),

#         # YOLO detector using compressed image directly.
#         # Input:
#         #   /gripper_camera/image_raw/compressed
#         # Output:
#         #   /flower_detector/detections
#         #   /flower_detector/image_annotated
#         Node(
#             package='flower_detector',
#             executable='yolo_flower_detector',
#             name='yolo_flower_detector',
#             output='screen',
#             parameters=[{
#                 'model_path': model_path,
#                 'image_topic': '/gripper_camera/image_raw/compressed',
#                 'confidence': confidence,
#                 'use_compressed': True,
#             }],
#         ),

#         # Combined visualizer.
#         # Input:
#         #   /flower_detector/image_annotated
#         #   /flower_detector/detections
#         #   /gripper_camera/tags
#         # Output:
#         #   /perception/image_combined
#         Node(
#             package='flower_detector',
#             executable='combined_visualizer',
#             name='combined_visualizer',
#             output='screen',
#             parameters=[{
#                 'image_topic': '/gripper_camera/image_raw/compressed',#/flower_detector/image_annotated
#                 'flower_topic': '/flower_detector/detections',
#                 'tag_topic': '/gripper_camera/tags',
#                 'output_topic': '/perception/image_combined',
#                 'use_compressed': True, #False
#             }],
#         ),

#         # Greenhouse information reader from detected AprilTag IDs.
#         # Input:
#         #   /gripper_camera/tags
#         # Service call:
#         #   /greenhouse_bridge/get_tag_reading
#         # Output:
#         #   /greenhouse/tag_reading
#         Node(
#             package='flower_detector',
#             executable='greenhouse_tag_reader',
#             name='greenhouse_tag_reader',
#             output='screen',
#             parameters=[{
#                 'tag_topic': '/gripper_camera/tags',
#                 'service_name': '/greenhouse_bridge/get_tag_reading',
#                 'cooldown_sec': 2.0,
#             }],
#         ),

#         # Snapshot saver.
#         # Input:
#         #   /perception/image_combined
#         # Service:
#         #   /save_perception_snapshot
#         # Output:
#         #   saved PNG file path
#         Node(
#             package='flower_detector',
#             executable='perception_snapshot_saver',
#             name='perception_snapshot_saver',
#             output='screen',
#             parameters=[{
#                 'image_topic': '/perception/image_combined',
#                 'lengths_topic': '/flower_detector/flower_lengths',
#                 'tag_reading_topic': '/greenhouse/tag_reading',
#                 'snapshot_dir': '/home/nikolaos/ros2_ws/perception_snapshots',
#             }],
#         ),

#         # Flower length estimator.
#         # Uses YOLO bounding-box height in pixels.
#         # If an AprilTag is visible, it estimates cm_per_pixel from the tag size.
#         # Input:
#         #   /flower_detector/detections
#         #   /gripper_camera/tags
#         # Output:
#         #   /flower_detector/flower_lengths
#         Node(
#             package='flower_detector',
#             executable='flower_length_estimator',
#             name='flower_length_estimator',
#             output='screen',
#             parameters=[{
#                 'detections_topic': '/flower_detector/detections',
#                 'tag_topic': '/gripper_camera/tags',
#                 'measurements_topic': '/flower_detector/flower_lengths',
#                 'cm_per_pixel': 0.0,
#                 'tag_size_cm': 4.0,
#             }],
#         ),
#     ])

#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, EnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    model_path = LaunchConfiguration('model_path')
    confidence = LaunchConfiguration('confidence')
    snapshot_dir = LaunchConfiguration('snapshot_dir')

    return LaunchDescription([
        DeclareLaunchArgument(
            'model_path',
            default_value=PathJoinSubstitution([
                FindPackageShare('flower_detector'),
                'models',
                'best.pt'
            ]),
            description='Path to the YOLO flower detector weights'
        ),

        DeclareLaunchArgument(
            'confidence',
            default_value='0.50',
            description='YOLO confidence threshold'
        ),

        DeclareLaunchArgument(
            'snapshot_dir',
            default_value=PathJoinSubstitution([
                EnvironmentVariable('HOME'),
                'ros2_ws',
                'perception_snapshots'
            ]),
            description='Directory where perception snapshots and JSON metadata are saved'
        ),

        # Greenhouse bridge.
        # Provides:
        #   /greenhouse_bridge/get_tag_reading
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                PathJoinSubstitution([
                    FindPackageShare('lupin_greenhouse_bridge'),
                    'launch',
                    'greenhouse_bridge.launch.py'
                ])
            ])
        ),

        # Decode compressed Wi-Fi image stream into a local raw image topic.
        # Input:
        #   /gripper_camera/image_raw/compressed
        # Output:
        #   /gripper_camera/image_raw_decoded
        Node(
            package='image_transport',
            executable='republish',
            name='compressed_to_raw_republisher',
            output='screen',
            arguments=['compressed', 'raw'],
            remappings=[
                ('in/compressed', '/gripper_camera/image_raw/compressed'),
                ('out', '/gripper_camera/image_raw_decoded'),
            ],
        ),

        # AprilTag detector using decoded raw image.
        # Input:
        #   /gripper_camera/image_raw_decoded
        # Output:
        #   /gripper_camera/tags
        #   /gripper_camera/image_tags
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
                'image': 'image_raw_decoded',
                'image_transport': 'raw',
                'type': 'umich',
                'tag_family': 'tf36h11',
            }.items()
        ),

        # YOLO detector using compressed image directly.
        # Input:
        #   /gripper_camera/image_raw/compressed
        # Output:
        #   /flower_detector/detections
        #   /flower_detector/image_annotated
        Node(
            package='flower_detector',
            executable='yolo_flower_detector',
            name='yolo_flower_detector',
            output='screen',
            parameters=[{
                'model_path': model_path,
                'image_topic': '/gripper_camera/image_raw/compressed',
                'confidence': confidence,
                'use_compressed': True,
            }],
        ),

        # Combined visualizer.
        # Input:
        #   /gripper_camera/image_raw/compressed
        #   /flower_detector/detections
        #   /gripper_camera/tags
        # Output:
        #   /perception/image_combined
        Node(
            package='flower_detector',
            executable='combined_visualizer',
            name='combined_visualizer',
            output='screen',
            parameters=[{
                'image_topic': '/gripper_camera/image_raw/compressed',
                'flower_topic': '/flower_detector/detections',
                'tag_topic': '/gripper_camera/tags',
                'output_topic': '/perception/image_combined',
                'use_compressed': True,
            }],
        ),

        # Greenhouse information reader from detected AprilTag IDs.
        # Input:
        #   /gripper_camera/tags
        # Service call:
        #   /greenhouse_bridge/get_tag_reading
        # Output:
        #   /greenhouse/tag_reading
        Node(
            package='flower_detector',
            executable='greenhouse_tag_reader',
            name='greenhouse_tag_reader',
            output='screen',
            parameters=[{
                'tag_topic': '/gripper_camera/tags',
                'service_name': '/greenhouse_bridge/get_tag_reading',
                'cooldown_sec': 2.0,
            }],
        ),

        # Snapshot saver.
        # Input:
        #   /perception/image_combined
        #   /flower_detector/flower_lengths
        #   /greenhouse/tag_reading
        # Service:
        #   /save_perception_snapshot
        # Output:
        #   saved PNG + JSON metadata
        Node(
            package='flower_detector',
            executable='perception_snapshot_saver',
            name='perception_snapshot_saver',
            output='screen',
            parameters=[{
                'image_topic': '/perception/image_combined',
                'lengths_topic': '/flower_detector/flower_lengths',
                'tag_reading_topic': '/greenhouse/tag_reading',
                'snapshot_dir': snapshot_dir,
            }],
        ),

        # Flower length estimator.
        # Uses YOLO bounding-box height in pixels.
        # If an AprilTag is visible, it estimates cm_per_pixel from the tag size.
        # Input:
        #   /flower_detector/detections
        #   /gripper_camera/tags
        # Output:
        #   /flower_detector/flower_lengths
        Node(
            package='flower_detector',
            executable='flower_length_estimator',
            name='flower_length_estimator',
            output='screen',
            parameters=[{
                'detections_topic': '/flower_detector/detections',
                'tag_topic': '/gripper_camera/tags',
                'measurements_topic': '/flower_detector/flower_lengths',
                'cm_per_pixel': 0.0,
                'tag_size_cm': 4.0,
            }],
        ),
    ])