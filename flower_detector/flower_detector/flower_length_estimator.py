#!/usr/bin/env python3

import json
import math

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from vision_msgs.msg import Detection2DArray
from apriltag_msgs.msg import AprilTagDetectionArray


class FlowerLengthEstimator(Node):
    def __init__(self):
        super().__init__('flower_length_estimator')

        self.declare_parameter('detections_topic', '/flower_detector/detections')
        self.declare_parameter('tag_topic', '/gripper_camera/tags')
        self.declare_parameter('measurements_topic', '/flower_detector/flower_lengths')

        # Static fallback scale. Keep 0.0 to use AprilTag scale dynamically.
        self.declare_parameter('cm_per_pixel', 0.0)

        # Real AprilTag side length in cm.
        # If your tag size is 0.162 m, then tag_size_cm = 16.2.
        self.declare_parameter('tag_size_cm', 16.2)

        self.detections_topic = self.get_parameter('detections_topic').value
        self.tag_topic = self.get_parameter('tag_topic').value
        self.measurements_topic = self.get_parameter('measurements_topic').value
        self.cm_per_pixel = float(self.get_parameter('cm_per_pixel').value)
        self.tag_size_cm = float(self.get_parameter('tag_size_cm').value)

        self.dynamic_cm_per_pixel = None
        self.last_tag_id = None
        self.last_tag_height_px = None

        self.detections_sub = self.create_subscription(
            Detection2DArray,
            self.detections_topic,
            self.detections_callback,
            10
        )

        self.tag_sub = self.create_subscription(
            AprilTagDetectionArray,
            self.tag_topic,
            self.tag_callback,
            10
        )

        self.measurements_pub = self.create_publisher(
            String,
            self.measurements_topic,
            10
        )

        self.get_logger().info(f'Subscribing detections: {self.detections_topic}')
        self.get_logger().info(f'Subscribing AprilTags: {self.tag_topic}')
        self.get_logger().info(f'Publishing flower lengths: {self.measurements_topic}')
        self.get_logger().info(f'Static cm_per_pixel fallback: {self.cm_per_pixel}')
        self.get_logger().info(f'AprilTag size: {self.tag_size_cm} cm')

    def distance_px(self, p1, p2):
        return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    def tag_callback(self, msg: AprilTagDetectionArray):
        if not msg.detections:
            return

        # Use the first visible AprilTag as scale reference.
        detection = msg.detections[0]
        corners = detection.corners

        if len(corners) != 4:
            self.get_logger().warn('AprilTag detection does not have 4 corners.')
            return

        # Estimate pixel height as average of left and right tag edges.
        left_height_px = self.distance_px(corners[0], corners[3])
        right_height_px = self.distance_px(corners[1], corners[2])
        tag_height_px = (left_height_px + right_height_px) / 2.0

        if tag_height_px <= 0.0:
            return

        self.dynamic_cm_per_pixel = self.tag_size_cm / tag_height_px
        self.last_tag_id = detection.id
        self.last_tag_height_px = tag_height_px

        self.get_logger().info(
            f'Updated scale from AprilTag {detection.id}: '
            f'tag_height_px={tag_height_px:.2f}, '
            f'cm_per_pixel={self.dynamic_cm_per_pixel:.4f}'
        )

    def get_active_scale(self):
        if self.cm_per_pixel > 0.0:
            return self.cm_per_pixel, 'static'

        if self.dynamic_cm_per_pixel is not None:
            return self.dynamic_cm_per_pixel, 'apriltag'

        return None, 'none'

    def detections_callback(self, msg: Detection2DArray):
        scale, scale_source = self.get_active_scale()
        flowers = []

        for index, detection in enumerate(msg.detections):
            if not detection.results:
                continue

            best_result = detection.results[0]
            class_id = best_result.hypothesis.class_id
            score = float(best_result.hypothesis.score)

            bbox = detection.bbox

            center_x_px = float(bbox.center.position.x)
            center_y_px = float(bbox.center.position.y)
            width_px = float(bbox.size_x)
            height_px = float(bbox.size_y)

            estimated_length_cm = None
            if scale is not None:
                estimated_length_cm = height_px * scale

            flower = {
                'id': index,
                'class_id': class_id,
                'score': score,
                'center_x_px': center_x_px,
                'center_y_px': center_y_px,
                'width_px': width_px,
                'height_px': height_px,
                'estimated_length_px': height_px,
                'estimated_length_cm': estimated_length_cm,
            }

            flowers.append(flower)

        output = {
            'stamp': {
                'sec': msg.header.stamp.sec,
                'nanosec': msg.header.stamp.nanosec,
            },
            'frame_id': msg.header.frame_id,
            'flower_count': len(flowers),
            'scale': {
                'scale_source': scale_source,
                'cm_per_pixel': scale,
                'tag_size_cm': self.tag_size_cm,
                'last_tag_id': self.last_tag_id,
                'last_tag_height_px': self.last_tag_height_px,
            },
            'flowers': flowers,
        }

        out_msg = String()
        out_msg.data = json.dumps(output)
        self.measurements_pub.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = FlowerLengthEstimator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
