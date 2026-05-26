from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='mission_planner',
            executable='scan_action_server',
            name='scan_server',
            output='screen'
        ),

        Node(
            package='mission_planner',
            executable='Mission_Planner_node',
            name='mission_planner',
            output='screen'
        ),
    ])