#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32MultiArray
from mirte_msgs.srv import SetNeopixel


class LedController(Node):

    def __init__(self):
        super().__init__('led_controller')

        self.client = self.create_client(
            SetNeopixel,
            '/io/leds/leds/set_color'
        )

        self.client.wait_for_service()

        self.subscription = self.create_subscription(
            Int32MultiArray,
            '/led/color_request',
            self.color_callback,
            10
        )

        self.get_logger().info('LED controller ready.')

    def color_callback(self, msg):
        r, g, b = msg.data

        request = SetNeopixel.Request()
        request.color.r = r
        request.color.g = g
        request.color.b = b

        self.client.call_async(request)

        self.get_logger().info(
            f'Set LED: ({r}, {g}, {b})'
        )


def main(args=None):
    rclpy.init(args=args)

    node = LedController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
