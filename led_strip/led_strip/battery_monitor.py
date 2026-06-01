#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import BatteryState
from std_msgs.msg import Int32MultiArray


class BatteryMonitor(Node):

    def __init__(self):
        super().__init__('battery_monitor')

        self.threshold = 0.30
        self.current_state = None

        self.publisher = self.create_publisher(
            Int32MultiArray,
            '/led/color_request',
            10
        )

        self.subscription = self.create_subscription(
            BatteryState,
            '/io/power/power_watcher',
            self.battery_callback,
            10
        )

    def battery_callback(self, msg):

        percentage = msg.percentage

        if percentage < self.threshold:
            desired = 'red'
            rgb = [255, 0, 0]
        else:
            desired = 'green'
            rgb = [0, 255, 0]

        if desired != self.current_state:
            message = Int32MultiArray()
            message.data = rgb

            self.publisher.publish(message)

            self.current_state = desired

            self.get_logger().info(
                f'Battery state → {desired}'
            )


def main(args=None):
    rclpy.init(args=args)

    node = BatteryMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
