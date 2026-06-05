#!/usr/bin/env python3

import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class LatestObservationPublisher(Node):
    def __init__(self):
        super().__init__('latest_observation_publisher')

        self.declare_parameter(
            'snapshot_dir',
            str(Path.home() / 'ros2_ws' / 'perception_snapshots')
        )
        self.declare_parameter('publish_topic', '/latest_observation')
        self.declare_parameter('publish_rate_hz', 1.0)
        self.declare_parameter('base_url', 'http://localhost:8088')

        self.snapshot_dir = Path(self.get_parameter('snapshot_dir').value)
        self.publish_topic = self.get_parameter('publish_topic').value
        self.publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.base_url = self.get_parameter('base_url').value.rstrip('/')

        self.publisher = self.create_publisher(String, self.publish_topic, 10)
        self.last_published_json_path = None

        self.timer = self.create_timer(
            1.0 / self.publish_rate_hz,
            self.timer_callback
        )

        self.get_logger().info(f'Watching snapshot directory: {self.snapshot_dir}')
        self.get_logger().info(f'Publishing latest observation on: {self.publish_topic}')
        self.get_logger().info(f'Base URL for dashboard: {self.base_url}')

    def find_latest_json(self):
        if not self.snapshot_dir.exists():
            return None

        json_files = list(self.snapshot_dir.glob('perception_snapshot_*.json'))
        if not json_files:
            return None

        return max(json_files, key=lambda path: path.stat().st_mtime)

    def timer_callback(self):
        latest_json_path = self.find_latest_json()

        if latest_json_path is None:
            return

        if self.last_published_json_path == str(latest_json_path):
            return

        try:
            with open(latest_json_path, 'r') as file:
                metadata = json.load(file)
        except Exception as error:
            self.get_logger().error(f'Failed to read {latest_json_path}: {error}')
            return

        image_path = metadata.get('image_path')
        if image_path is None:
            image_path = str(latest_json_path.with_suffix('.png'))

        image_path = Path(image_path)

        output = {
            'image_path': str(image_path),
            'json_path': str(latest_json_path),
            'image_url': f'{self.base_url}/{image_path.name}',
            'json_url': f'{self.base_url}/{latest_json_path.name}',
            'metadata': metadata,
        }

        msg = String()
        msg.data = json.dumps(output)

        self.publisher.publish(msg)
        self.last_published_json_path = str(latest_json_path)

        self.get_logger().info(
            f'Published latest observation: {image_path.name}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = LatestObservationPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
