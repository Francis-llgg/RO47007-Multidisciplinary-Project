#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ScanSelfFilterNode(Node):
    def __init__(self):
        super().__init__("scan_self_filter_node")

        self.declare_parameter("input_scan_topic", "/scan")
        self.declare_parameter("output_scan_topic", "/scan_filtered")

        # Lidar points closer than this radius will be removed.
        self.declare_parameter("self_clear_radius", 0.15)

        input_topic = self.get_parameter("input_scan_topic").value
        output_topic = self.get_parameter("output_scan_topic").value
        self.self_clear_radius = float(
            self.get_parameter("self_clear_radius").value
        )

        self.sub = self.create_subscription(
            LaserScan,
            input_topic,
            self.scan_callback,
            10,
        )

        self.pub = self.create_publisher(
            LaserScan,
            output_topic,
            10,
        )

        self.get_logger().info(f"Scan filter: {input_topic} -> {output_topic}")
        self.get_logger().info(
            f"Removing points closer than {self.self_clear_radius:.2f} m"
        )

    def scan_callback(self, msg: LaserScan):
        filtered = LaserScan()
        filtered.header = msg.header
        filtered.angle_min = msg.angle_min
        filtered.angle_max = msg.angle_max
        filtered.angle_increment = msg.angle_increment
        filtered.time_increment = msg.time_increment
        filtered.scan_time = msg.scan_time
        filtered.range_min = msg.range_min
        filtered.range_max = msg.range_max
        filtered.intensities = msg.intensities

        filtered_ranges = list(msg.ranges)

        removed_count = 0

        for i, r in enumerate(filtered_ranges):
            if not math.isfinite(r):
                continue

            # Delete points closer than self_clear_radius (likely robot self)
            if r < self.self_clear_radius:
                filtered_ranges[i] = float("inf")
                removed_count += 1

        filtered.ranges = filtered_ranges
        self.pub.publish(filtered)

        if removed_count > 0:
            self.get_logger().debug(
                f"Removed {removed_count} points < {self.self_clear_radius:.2f} m"
            )


def main(args=None):
    rclpy.init(args=args)
    node = ScanSelfFilterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()