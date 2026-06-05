#!/usr/bin/env python3

import cv2
import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CompressedImage


class CompressedImageRepublisher(Node):
    def __init__(self):
        super().__init__('compressed_image_republisher')

        self.declare_parameter('input_topic', '/gripper_camera/image_raw')
        self.declare_parameter('output_topic', '/gripper_camera/image_raw/compressed')
        self.declare_parameter('jpeg_quality', 60)

        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.jpeg_quality = int(self.get_parameter('jpeg_quality').value)

        self.bridge = CvBridge()

        self.sub = self.create_subscription(
            Image,
            self.input_topic,
            self.image_callback,
            10
        )

        self.pub = self.create_publisher(
            CompressedImage,
            self.output_topic,
            10
        )

        self.get_logger().info(f'Subscribing raw image: {self.input_topic}')
        self.get_logger().info(f'Publishing compressed image: {self.output_topic}')
        self.get_logger().info(f'JPEG quality: {self.jpeg_quality}')

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Image conversion failed: {e}')
            return

        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
        success, encoded_image = cv2.imencode('.jpg', frame, encode_params)

        if not success:
            self.get_logger().error('JPEG compression failed')
            return

        compressed_msg = CompressedImage()
        compressed_msg.header = msg.header
        compressed_msg.format = 'jpeg'
        compressed_msg.data = encoded_image.tobytes()

        self.pub.publish(compressed_msg)


def main(args=None):
    rclpy.init(args=args)
    node = CompressedImageRepublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
