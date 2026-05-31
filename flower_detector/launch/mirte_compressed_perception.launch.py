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

#         # AprilTag detector using compressed image transport.
#         # Input:
#         #   /gripper_camera/image_raw/compressed
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
#                 'image': 'image_raw',
#                 'image_transport': 'compressed',
#                 'type': 'umich',
#                 'tag_family': 'tf36h11',
#             }.items()
#         ),

#         # YOLO detector using compressed image topic.
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

#         # Combined visualizer using compressed image topic.
#         Node(
#             package='flower_detector',
#             executable='combined_visualizer',
#             name='combined_visualizer',
#             output='screen',
#             parameters=[{
#                 'image_topic': '/gripper_camera/image_raw/compressed',
#                 'flower_topic': '/flower_detector/detections',
#                 'tag_topic': '/gripper_camera/tags',
#                 'output_topic': '/perception/image_combined',
#                 'use_compressed': True,
#             }],
#         ),
#     ])



# #### detection combined with wifi no april tag readings########
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

#         # Combined visualizer using YOLO annotated raw image as base image.
#         # This avoids decoding compressed images twice inside custom nodes.
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
#     ])


# #### detection combined with wifi + AprilTag greenhouse readings ########
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

#         # Combined visualizer using YOLO annotated raw image as base image.
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

#         # Greenhouse information reader.
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
#     ])


# #### detection combined with wifi + AprilTag greenhouse readings ######## last try before i went off
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

#         # Combined visualizer using YOLO annotated raw image as base image.
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
#     ])

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

        # Combined visualizer using YOLO annotated raw image as base image.
        # Input:
        #   /flower_detector/image_annotated
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
                'image_topic': '/flower_detector/image_annotated',
                'flower_topic': '/flower_detector/detections',
                'tag_topic': '/gripper_camera/tags',
                'output_topic': '/perception/image_combined',
                'use_compressed': False,
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
    ])