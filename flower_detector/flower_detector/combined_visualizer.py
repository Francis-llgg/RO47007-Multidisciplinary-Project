# #!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node

# from sensor_msgs.msg import Image
# from vision_msgs.msg import Detection2DArray
# from apriltag_msgs.msg import AprilTagDetectionArray
# from cv_bridge import CvBridge

# import cv2
# import numpy as np


# # OpenCV uses BGR color order, not RGB.
# CLASS_COLORS = {
#     'tulip_red': (255, 0, 0),        # blue
#     'tulip_white': (255, 255, 0),    # cyan
#     'tulip_pink': (180, 180, 180),   # light gray
#     'bug': (255, 255, 0),            # cyan
# }

# DEFAULT_DETECTION_COLOR = (0, 255, 0)   # green fallback
# APRILTAG_COLOR = (0, 0, 255)            # red


# class CombinedVisualizer(Node):
#     def __init__(self):
#         super().__init__('combined_visualizer')

#         self.declare_parameter('image_topic', '/camera/image_raw')
#         self.declare_parameter('flower_topic', '/flower_detector/detections')
#         self.declare_parameter('tag_topic', '/camera/tags')
#         self.declare_parameter('output_topic', '/perception/image_combined')

#         self.image_topic = self.get_parameter('image_topic').value
#         self.flower_topic = self.get_parameter('flower_topic').value
#         self.tag_topic = self.get_parameter('tag_topic').value
#         self.output_topic = self.get_parameter('output_topic').value

#         self.bridge = CvBridge()

#         self.latest_flowers = None
#         self.latest_tags = None

#         self.image_sub = self.create_subscription(
#             Image,
#             self.image_topic,
#             self.image_callback,
#             10
#         )

#         self.flower_sub = self.create_subscription(
#             Detection2DArray,
#             self.flower_topic,
#             self.flower_callback,
#             10
#         )

#         self.tag_sub = self.create_subscription(
#             AprilTagDetectionArray,
#             self.tag_topic,
#             self.tag_callback,
#             10
#         )

#         self.image_pub = self.create_publisher(
#             Image,
#             self.output_topic,
#             10
#         )

#         self.get_logger().info('Combined visualizer started')
#         self.get_logger().info(f'Subscribing image: {self.image_topic}')
#         self.get_logger().info(f'Subscribing flowers: {self.flower_topic}')
#         self.get_logger().info(f'Subscribing AprilTags: {self.tag_topic}')
#         self.get_logger().info(f'Publishing combined image: {self.output_topic}')

#     def flower_callback(self, msg):
#         self.latest_flowers = msg

#     def tag_callback(self, msg):
#         self.latest_tags = msg

#     def image_callback(self, msg):
#         try:
#             frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
#         except Exception as e:
#             self.get_logger().error(f'Image conversion failed: {e}')
#             return

#         output = frame.copy()

#         self.draw_flowers(output)
#         self.draw_apriltags(output)

#         try:
#             out_msg = self.bridge.cv2_to_imgmsg(output, encoding='bgr8')
#             out_msg.header = msg.header
#             self.image_pub.publish(out_msg)
#         except Exception as e:
#             self.get_logger().error(f'Failed to publish combined image: {e}')

#     def draw_flowers(self, image):
#         if self.latest_flowers is None:
#             return

#         for detection in self.latest_flowers.detections:
#             cx = detection.bbox.center.position.x
#             cy = detection.bbox.center.position.y
#             w = detection.bbox.size_x
#             h = detection.bbox.size_y

#             x1 = int(cx - w / 2.0)
#             y1 = int(cy - h / 2.0)
#             x2 = int(cx + w / 2.0)
#             y2 = int(cy + h / 2.0)

#             label = 'unknown'
#             score = 0.0

#             if len(detection.results) > 0:
#                 label = detection.results[0].hypothesis.class_id
#                 score = detection.results[0].hypothesis.score

#             color = CLASS_COLORS.get(label, DEFAULT_DETECTION_COLOR)

#             cv2.rectangle(
#                 image,
#                 (x1, y1),
#                 (x2, y2),
#                 color,
#                 3
#             )

#             text = f'{label} {score:.2f}'

#             cv2.putText(
#                 image,
#                 text,
#                 (x1, max(y1 - 8, 25)),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.8,
#                 color,
#                 2
#             )

#     def draw_apriltags(self, image):
#         if self.latest_tags is None:
#             return

#         for tag in self.latest_tags.detections:
#             corners = []

#             for corner in tag.corners:
#                 corners.append((int(corner.x), int(corner.y)))

#             if len(corners) == 4:
#                 points = np.array(corners, dtype=np.int32)
#                 cv2.polylines(
#                     image,
#                     [points],
#                     isClosed=True,
#                     color=APRILTAG_COLOR,
#                     thickness=3
#                 )

#             cx = int(tag.centre.x)
#             cy = int(tag.centre.y)

#             cv2.circle(
#                 image,
#                 (cx, cy),
#                 6,
#                 APRILTAG_COLOR,
#                 -1
#             )

#             text = f'AprilTag {tag.id}'

#             cv2.putText(
#                 image,
#                 text,
#                 (cx + 10, cy - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.8,
#                 APRILTAG_COLOR,
#                 2
#             )


# def main(args=None):
#     rclpy.init(args=args)

#     node = CombinedVisualizer()

#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass

#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main()



#!/usr/bin/env python3

import cv2
import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CompressedImage
from vision_msgs.msg import Detection2DArray
from apriltag_msgs.msg import AprilTagDetectionArray
from cv_bridge import CvBridge


CLASS_COLORS = {
    'tulip_red': (255, 0, 0),
    'tulip_white': (255, 255, 0),
    'tulip_pink': (180, 180, 180),
    'bug': (255, 255, 0),
}

DEFAULT_DETECTION_COLOR = (0, 255, 0)
APRILTAG_COLOR = (0, 0, 255)


class CombinedVisualizer(Node):
    def __init__(self):
        super().__init__('combined_visualizer')

        self.declare_parameter('image_topic', '/gripper_camera/image_raw')
        self.declare_parameter('flower_topic', '/flower_detector/detections')
        self.declare_parameter('tag_topic', '/gripper_camera/tags')
        self.declare_parameter('output_topic', '/perception/image_combined')
        self.declare_parameter('use_compressed', False)

        self.image_topic = self.get_parameter('image_topic').value
        self.flower_topic = self.get_parameter('flower_topic').value
        self.tag_topic = self.get_parameter('tag_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.use_compressed = bool(self.get_parameter('use_compressed').value)

        self.bridge = CvBridge()
        self.latest_flowers = None
        self.latest_tags = None

        image_msg_type = CompressedImage if self.use_compressed else Image

        self.image_sub = self.create_subscription(
            image_msg_type,
            self.image_topic,
            self.image_callback,
            10
        )

        self.flower_sub = self.create_subscription(
            Detection2DArray,
            self.flower_topic,
            self.flower_callback,
            10
        )

        self.tag_sub = self.create_subscription(
            AprilTagDetectionArray,
            self.tag_topic,
            self.tag_callback,
            10
        )

        self.image_pub = self.create_publisher(
            Image,
            self.output_topic,
            10
        )

        self.get_logger().info('Combined visualizer started')
        self.get_logger().info(f'Subscribing image: {self.image_topic}')
        self.get_logger().info(f'Using compressed input: {self.use_compressed}')
        self.get_logger().info(f'Subscribing flowers: {self.flower_topic}')
        self.get_logger().info(f'Subscribing AprilTags: {self.tag_topic}')
        self.get_logger().info(f'Publishing combined image: {self.output_topic}')

    def flower_callback(self, msg):
        self.latest_flowers = msg

    def tag_callback(self, msg):
        self.latest_tags = msg

    def image_callback(self, msg):
        try:
            if self.use_compressed:
                frame = self.compressed_msg_to_cv2(msg)
            else:
                frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Image conversion failed: {e}')
            return

        if frame is None:
            self.get_logger().error('Received empty frame')
            return

        output = frame.copy()

        self.draw_flowers(output)
        self.draw_apriltags(output)

        try:
            out_msg = self.bridge.cv2_to_imgmsg(output, encoding='bgr8')
            out_msg.header = msg.header
            self.image_pub.publish(out_msg)
        except Exception as e:
            self.get_logger().error(f'Failed to publish combined image: {e}')

    def compressed_msg_to_cv2(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            raise RuntimeError('Failed to decode compressed image')

        return frame

    def draw_flowers(self, image):
        if self.latest_flowers is None:
            return

        for detection in self.latest_flowers.detections:
            cx = detection.bbox.center.position.x
            cy = detection.bbox.center.position.y
            w = detection.bbox.size_x
            h = detection.bbox.size_y

            x1 = int(cx - w / 2.0)
            y1 = int(cy - h / 2.0)
            x2 = int(cx + w / 2.0)
            y2 = int(cy + h / 2.0)

            label = 'unknown'
            score = 0.0

            if len(detection.results) > 0:
                label = detection.results[0].hypothesis.class_id
                score = detection.results[0].hypothesis.score

            color = CLASS_COLORS.get(label, DEFAULT_DETECTION_COLOR)

            cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)

            text = f'{label} {score:.2f}'
            cv2.putText(
                image,
                text,
                (x1, max(y1 - 8, 25)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

    def draw_apriltags(self, image):
        if self.latest_tags is None:
            return

        for tag in self.latest_tags.detections:
            corners = []

            for corner in tag.corners:
                corners.append((int(corner.x), int(corner.y)))

            if len(corners) == 4:
                points = np.array(corners, dtype=np.int32)
                cv2.polylines(
                    image,
                    [points],
                    isClosed=True,
                    color=APRILTAG_COLOR,
                    thickness=3
                )

            cx = int(tag.centre.x)
            cy = int(tag.centre.y)

            cv2.circle(image, (cx, cy), 6, APRILTAG_COLOR, -1)

            text = f'AprilTag {tag.id}'
            cv2.putText(
                image,
                text,
                (cx + 10, cy - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                APRILTAG_COLOR,
                2
            )


def main(args=None):
    rclpy.init(args=args)

    node = CombinedVisualizer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()