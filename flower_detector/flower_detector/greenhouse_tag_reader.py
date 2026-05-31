#!/usr/bin/env python3

import json
import rclpy
from rclpy.node import Node

from apriltag_msgs.msg import AprilTagDetectionArray
from std_msgs.msg import String
from lupin_greenhouse_msgs.srv import GetTagReading


class GreenhouseTagReader(Node):
    def __init__(self):
        super().__init__('greenhouse_tag_reader')

        self.declare_parameter('tag_topic', '/gripper_camera/tags')
        self.declare_parameter('service_name', '/greenhouse_bridge/get_tag_reading')
        self.declare_parameter('cooldown_sec', 2.0)

        self.tag_topic = self.get_parameter('tag_topic').value
        self.service_name = self.get_parameter('service_name').value
        self.cooldown_sec = float(self.get_parameter('cooldown_sec').value)

        self.last_query_time = {}

        self.client = self.create_client(GetTagReading, self.service_name)

        self.tag_sub = self.create_subscription(
            AprilTagDetectionArray,
            self.tag_topic,
            self.tag_callback,
            10
        )

        self.reading_pub = self.create_publisher(
            String,
            '/greenhouse/tag_reading',
            10
        )

        self.get_logger().info(f'Subscribing to AprilTags: {self.tag_topic}')
        self.get_logger().info(f'Calling greenhouse service: {self.service_name}')
        self.get_logger().info('Publishing readings on: /greenhouse/tag_reading')

    def tag_callback(self, msg: AprilTagDetectionArray):
        if not msg.detections:
            return

        now = self.get_clock().now().nanoseconds / 1e9

        for detection in msg.detections:
            tag_id = str(detection.id)

            last_time = self.last_query_time.get(tag_id, 0.0)
            if now - last_time < self.cooldown_sec:
                continue

            self.last_query_time[tag_id] = now
            self.query_greenhouse(tag_id)

    def query_greenhouse(self, tag_id: str):
        if not self.client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warn(f'Service not available: {self.service_name}')
            return

        request = GetTagReading.Request()
        request.tag_id = tag_id

        self.get_logger().info(f'Requesting greenhouse reading for tag_id={tag_id}')

        future = self.client.call_async(request)
        future.add_done_callback(
            lambda future_result, tid=tag_id: self.handle_response(future_result, tid)
        )

    def handle_response(self, future, tag_id: str):
        try:
            response = future.result()
        except Exception as error:
            self.get_logger().error(f'Failed reading for tag {tag_id}: {error}')
            return

        if response.status != response.STATUS_OK:
            self.get_logger().warn(
                f'Tag {tag_id} returned error: {response.error_message}'
            )
            return

        reading = response.reading

        output = {
            'tag_id': reading.tag_id,
            'stamp': {
                'sec': reading.stamp.sec,
                'nanosec': reading.stamp.nanosec,
            },
            'sim_time_of_day_seconds': reading.sim_time_of_day_seconds,
            'readings': [
                {
                    'name': sensor.name,
                    'value': sensor.value,
                }
                for sensor in reading.readings
            ],
        }

        msg = String()
        msg.data = json.dumps(output)

        self.reading_pub.publish(msg)
        self.get_logger().info(f'Published greenhouse reading for tag {tag_id}: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = GreenhouseTagReader()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
