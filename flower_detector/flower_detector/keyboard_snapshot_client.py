#!/usr/bin/env python3

import sys
import select
import termios
import tty

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class KeyboardSnapshotClient(Node):
    def __init__(self):
        super().__init__('keyboard_snapshot_client')

        self.client = self.create_client(Trigger, '/save_perception_snapshot')

        self.get_logger().info('Keyboard snapshot client started.')
        self.get_logger().info("Press 's' to save a perception snapshot.")
        self.get_logger().info("Press 'q' to quit.")

    def call_snapshot_service(self):
        if not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Service /save_perception_snapshot is not available.')
            return

        request = Trigger.Request()
        future = self.client.call_async(request)
        future.add_done_callback(self.handle_response)

    def handle_response(self, future):
        try:
            response = future.result()
        except Exception as error:
            self.get_logger().error(f'Snapshot service call failed: {error}')
            return

        if response.success:
            self.get_logger().info(f'Snapshot saved: {response.message}')
        else:
            self.get_logger().warn(f'Snapshot not saved: {response.message}')


def get_key(timeout=0.1):
    readable, _, _ = select.select([sys.stdin], [], [], timeout)
    if readable:
        return sys.stdin.read(1)
    return None


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardSnapshotClient()

    old_settings = termios.tcgetattr(sys.stdin)

    try:
        tty.setcbreak(sys.stdin.fileno())

        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)

            key = get_key(timeout=0.05)

            if key == 's':
                node.get_logger().info("Pressed 's': saving snapshot...")
                node.call_snapshot_service()

            elif key == 'q':
                node.get_logger().info("Pressed 'q': exiting.")
                break

    except KeyboardInterrupt:
        pass

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
