import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # LED controller node
    led_controller = Node(
        package="led_strip",
        executable="led_controller",
        output="screen"
    )

    # Battery monitor node
    battery_monitor = Node(
        package="led_strip",
        executable="battery_monitor",
        output="screen"
    )

    return LaunchDescription([
        led_controller,
        battery_monitor
    ])

