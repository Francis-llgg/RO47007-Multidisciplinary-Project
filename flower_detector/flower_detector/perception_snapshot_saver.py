# #!/usr/bin/env python3

# import os
# from datetime import datetime
# from pathlib import Path

# import cv2
# import rclpy
# from cv_bridge import CvBridge
# from rclpy.node import Node

# from sensor_msgs.msg import Image
# from std_srvs.srv import Trigger


# class PerceptionSnapshotSaver(Node):
#     def __init__(self):
#         super().__init__('perception_snapshot_saver')

#         self.declare_parameter('image_topic', '/perception/image_combined')
#         self.declare_parameter(
#             'snapshot_dir',
#             str(Path.home() / 'ros2_ws' / 'perception_snapshots')
#         )

#         self.image_topic = self.get_parameter('image_topic').value
#         self.snapshot_dir = self.get_parameter('snapshot_dir').value

#         os.makedirs(self.snapshot_dir, exist_ok=True)

#         self.bridge = CvBridge()
#         self.latest_image = None
#         self.latest_stamp = None

#         self.image_sub = self.create_subscription(
#             Image,
#             self.image_topic,
#             self.image_callback,
#             10
#         )

#         self.save_service = self.create_service(
#             Trigger,
#             '/save_perception_snapshot',
#             self.save_snapshot_callback
#         )

#         self.get_logger().info(f'Subscribing to image topic: {self.image_topic}')
#         self.get_logger().info(f'Snapshot directory: {self.snapshot_dir}')
#         self.get_logger().info('Service available: /save_perception_snapshot')

#     def image_callback(self, msg: Image):
#         try:
#             self.latest_image = self.bridge.imgmsg_to_cv2(
#                 msg,
#                 desired_encoding='bgr8'
#             )
#             self.latest_stamp = msg.header.stamp
#         except Exception as error:
#             self.get_logger().error(f'Failed to convert image: {error}')

#     def save_snapshot_callback(self, request, response):
#         if self.latest_image is None:
#             response.success = False
#             response.message = 'No perception image received yet.'
#             return response

#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         filename = f'perception_snapshot_{timestamp}.png'
#         filepath = os.path.join(self.snapshot_dir, filename)

#         try:
#             success = cv2.imwrite(filepath, self.latest_image)
#         except Exception as error:
#             response.success = False
#             response.message = f'Failed to save image: {error}'
#             return response

#         if not success:
#             response.success = False
#             response.message = f'cv2.imwrite failed for path: {filepath}'
#             return response

#         response.success = True
#         response.message = filepath

#         self.get_logger().info(f'Saved perception snapshot: {filepath}')
#         return response


# def main(args=None):
#     rclpy.init(args=args)
#     node = PerceptionSnapshotSaver()

#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass

#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main()



#!/usr/bin/env python3

# import json
# import os
# from datetime import datetime
# from pathlib import Path

# import cv2
# import rclpy
# from cv_bridge import CvBridge
# from rclpy.node import Node

# from sensor_msgs.msg import Image
# from std_msgs.msg import String
# from std_srvs.srv import Trigger


# class PerceptionSnapshotSaver(Node):
#     def __init__(self):
#         super().__init__('perception_snapshot_saver')

#         self.declare_parameter('image_topic', '/perception/image_combined')
#         self.declare_parameter('lengths_topic', '/flower_detector/flower_lengths')
#         self.declare_parameter(
#             'snapshot_dir',
#             str(Path.home() / 'ros2_ws' / 'perception_snapshots')
#         )

#         self.image_topic = self.get_parameter('image_topic').value
#         self.lengths_topic = self.get_parameter('lengths_topic').value
#         self.snapshot_dir = self.get_parameter('snapshot_dir').value

#         os.makedirs(self.snapshot_dir, exist_ok=True)

#         self.bridge = CvBridge()

#         self.latest_image = None
#         self.latest_image_stamp = None

#         self.latest_lengths_json = None
#         self.latest_lengths_stamp = None

#         self.image_sub = self.create_subscription(
#             Image,
#             self.image_topic,
#             self.image_callback,
#             10
#         )

#         self.lengths_sub = self.create_subscription(
#             String,
#             self.lengths_topic,
#             self.lengths_callback,
#             10
#         )

#         self.save_service = self.create_service(
#             Trigger,
#             '/save_perception_snapshot',
#             self.save_snapshot_callback
#         )

#         self.get_logger().info(f'Subscribing image topic: {self.image_topic}')
#         self.get_logger().info(f'Subscribing lengths topic: {self.lengths_topic}')
#         self.get_logger().info(f'Snapshot directory: {self.snapshot_dir}')
#         self.get_logger().info('Service available: /save_perception_snapshot')

#     def image_callback(self, msg: Image):
#         try:
#             self.latest_image = self.bridge.imgmsg_to_cv2(
#                 msg,
#                 desired_encoding='bgr8'
#             )
#             self.latest_image_stamp = {
#                 'sec': msg.header.stamp.sec,
#                 'nanosec': msg.header.stamp.nanosec,
#                 'frame_id': msg.header.frame_id,
#             }
#         except Exception as error:
#             self.get_logger().error(f'Failed to convert image: {error}')

#     def lengths_callback(self, msg: String):
#         self.latest_lengths_json = msg.data

#         try:
#             parsed = json.loads(msg.data)
#             self.latest_lengths_stamp = parsed.get('stamp', None)
#         except Exception:
#             self.latest_lengths_stamp = None

#     def save_snapshot_callback(self, request, response):
#         if self.latest_image is None:
#             response.success = False
#             response.message = 'No perception image received yet.'
#             return response

#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

#         image_filename = f'perception_snapshot_{timestamp}.png'
#         json_filename = f'perception_snapshot_{timestamp}.json'

#         image_path = os.path.join(self.snapshot_dir, image_filename)
#         json_path = os.path.join(self.snapshot_dir, json_filename)

#         try:
#             image_saved = cv2.imwrite(image_path, self.latest_image)
#         except Exception as error:
#             response.success = False
#             response.message = f'Failed to save image: {error}'
#             return response

#         if not image_saved:
#             response.success = False
#             response.message = f'cv2.imwrite failed for path: {image_path}'
#             return response

#         metadata = {
#             'snapshot_time': timestamp,
#             'image_path': image_path,
#             'image_stamp': self.latest_image_stamp,
#             'flower_lengths_raw': self.latest_lengths_json,
#             'flower_lengths_stamp': self.latest_lengths_stamp,
#         }

#         if self.latest_lengths_json is not None:
#             try:
#                 metadata['flower_lengths'] = json.loads(self.latest_lengths_json)
#             except Exception:
#                 metadata['flower_lengths'] = None
#         else:
#             metadata['flower_lengths'] = None

#         try:
#             with open(json_path, 'w') as file:
#                 json.dump(metadata, file, indent=2)
#         except Exception as error:
#             response.success = False
#             response.message = f'Image saved, but failed to save JSON: {error}'
#             return response

#         response.success = True
#         response.message = f'image={image_path}; json={json_path}'

#         self.get_logger().info(f'Saved perception image: {image_path}')
#         self.get_logger().info(f'Saved perception metadata: {json_path}')

#         return response


# def main(args=None):
#     rclpy.init(args=args)
#     node = PerceptionSnapshotSaver()

#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass

#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main()



#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path

import cv2
import rclpy
from rclpy.node import Node

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
from std_srvs.srv import Trigger


class PerceptionSnapshotSaver(Node):
    def __init__(self):
        super().__init__('perception_snapshot_saver')

        self.declare_parameter('image_topic', '/perception/image_combined')
        self.declare_parameter('lengths_topic', '/flower_detector/flower_lengths')
        self.declare_parameter('tag_reading_topic', '/greenhouse/tag_reading')
        self.declare_parameter(
            'snapshot_dir',
            '/home/nikolaos/ros2_ws/perception_snapshots'
        )

        self.image_topic = self.get_parameter('image_topic').value
        self.lengths_topic = self.get_parameter('lengths_topic').value
        self.tag_reading_topic = self.get_parameter('tag_reading_topic').value
        self.snapshot_dir = Path(self.get_parameter('snapshot_dir').value)

        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        self.bridge = CvBridge()

        self.latest_image_msg = None
        self.latest_image = None
        self.latest_lengths = None
        self.latest_tag_reading = None

        self.image_sub = self.create_subscription(
            Image,
            self.image_topic,
            self.image_callback,
            10
        )

        self.lengths_sub = self.create_subscription(
            String,
            self.lengths_topic,
            self.lengths_callback,
            10
        )

        self.tag_reading_sub = self.create_subscription(
            String,
            self.tag_reading_topic,
            self.tag_reading_callback,
            10
        )

        self.save_srv = self.create_service(
            Trigger,
            '/save_perception_snapshot',
            self.save_snapshot_callback
        )

        self.get_logger().info('Perception snapshot saver started')
        self.get_logger().info(f'Subscribing image: {self.image_topic}')
        self.get_logger().info(f'Subscribing flower lengths: {self.lengths_topic}')
        self.get_logger().info(f'Subscribing tag readings: {self.tag_reading_topic}')
        self.get_logger().info(f'Snapshot directory: {self.snapshot_dir}')
        self.get_logger().info('Service available: /save_perception_snapshot')

    def image_callback(self, msg):
        self.latest_image_msg = msg

        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )
        except Exception as e:
            self.get_logger().error(f'Failed to convert image: {e}')
            self.latest_image = None

    def lengths_callback(self, msg):
        self.latest_lengths = self.parse_string_message(msg.data)

    def tag_reading_callback(self, msg):
        self.latest_tag_reading = self.parse_string_message(msg.data)

    def parse_string_message(self, data):
        """
        Tries to parse std_msgs/String as JSON.
        If it is not valid JSON, stores it as plain text.
        """
        if data is None:
            return None

        try:
            return json.loads(data)
        except Exception:
            return data

    def save_snapshot_callback(self, request, response):
        if self.latest_image is None:
            response.success = False
            response.message = 'No image received yet. Cannot save snapshot.'
            return response

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')

        image_filename = f'perception_snapshot_{timestamp}.png'
        json_filename = f'perception_snapshot_{timestamp}.json'

        image_path = self.snapshot_dir / image_filename
        json_path = self.snapshot_dir / json_filename

        try:
            cv2.imwrite(str(image_path), self.latest_image)
        except Exception as e:
            response.success = False
            response.message = f'Failed to save image: {e}'
            return response

        image_header = None
        if self.latest_image_msg is not None:
            image_header = {
                'frame_id': self.latest_image_msg.header.frame_id,
                'stamp_sec': int(self.latest_image_msg.header.stamp.sec),
                'stamp_nanosec': int(self.latest_image_msg.header.stamp.nanosec),
            }

        metadata = {
            'timestamp': timestamp,
            'image_file': image_filename,
            'image_path': str(image_path),
            'image_header': image_header,
            'flower_lengths': self.latest_lengths,
            'greenhouse_tag_reading': self.latest_tag_reading,
        }

        try:
            with open(json_path, 'w') as f:
                json.dump(metadata, f, indent=4)
        except Exception as e:
            response.success = False
            response.message = f'Image saved, but failed to save JSON: {e}'
            return response

        response.success = True
        response.message = f'Saved snapshot: {image_path} and {json_path}'

        self.get_logger().info(response.message)

        return response


def main(args=None):
    rclpy.init(args=args)

    node = PerceptionSnapshotSaver()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()