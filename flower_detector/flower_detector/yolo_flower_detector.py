#!/usr/bin/env python3

import cv2
import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CompressedImage
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge

from ultralytics import YOLO


class YoloFlowerDetector(Node):
    def __init__(self):
        super().__init__('yolo_flower_detector')

        self.declare_parameter(
            'model_path',
            '/home/nikolaos/mdp_flower_detection/runs/detect/train-2/weights/best.pt'
        )
        self.declare_parameter('image_topic', '/gripper_camera/image_raw')
        self.declare_parameter('confidence', 0.50)
        self.declare_parameter('use_compressed', False)

        self.model_path = self.get_parameter('model_path').value
        self.image_topic = self.get_parameter('image_topic').value
        self.confidence = float(self.get_parameter('confidence').value)
        self.use_compressed = bool(self.get_parameter('use_compressed').value)

        self.bridge = CvBridge()
        self.model = YOLO(self.model_path)

        image_msg_type = CompressedImage if self.use_compressed else Image

        self.image_sub = self.create_subscription(
            image_msg_type,
            self.image_topic,
            self.image_callback,
            10
        )

        self.detection_pub = self.create_publisher(
            Detection2DArray,
            '/flower_detector/detections',
            10
        )

        self.annotated_pub = self.create_publisher(
            Image,
            '/flower_detector/image_annotated',
            10
        )

        self.get_logger().info('YOLO flower detector started')
        self.get_logger().info(f'Model path: {self.model_path}')
        self.get_logger().info(f'Subscribing to: {self.image_topic}')
        self.get_logger().info(f'Using compressed input: {self.use_compressed}')
        self.get_logger().info('Publishing: /flower_detector/detections')
        self.get_logger().info('Publishing: /flower_detector/image_annotated')

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

        try:
            results = self.model(frame, conf=self.confidence, verbose=False)[0]
        except Exception as e:
            self.get_logger().error(f'YOLO inference failed: {e}')
            return

        detection_array = Detection2DArray()
        detection_array.header = msg.header

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detection = Detection2D()
            detection.header = msg.header

            detection.bbox.center.position.x = float((x1 + x2) / 2.0)
            detection.bbox.center.position.y = float((y1 + y2) / 2.0)
            detection.bbox.size_x = float(x2 - x1)
            detection.bbox.size_y = float(y2 - y1)

            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hypothesis.class_id = str(self.model.names[cls_id])
            hypothesis.hypothesis.score = conf

            detection.results.append(hypothesis)
            detection_array.detections.append(detection)

        annotated_frame = results.plot()
        annotated_msg = self.bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
        annotated_msg.header = msg.header

        self.detection_pub.publish(detection_array)
        self.annotated_pub.publish(annotated_msg)

    def compressed_msg_to_cv2(self, msg):
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            raise RuntimeError('Failed to decode compressed image')

        return frame


def main(args=None):
    rclpy.init(args=args)

    node = YoloFlowerDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
