import os

from ament_index_python import get_package_share_directory
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

from mdp_interfaces.action import Scan


class ScanActionServer(Node):

    def __init__(self):
        super().__init__('scan_action_server')
        self._action_server = ActionServer(
            self,
            Scan,
            'scan',
            self.execute_callback)
        
        self.bridge = CvBridge()
        self.latest_image = None
        
        self.image_sub = self.create_subscription(
			Image,
            '/camera/image_raw',
			# '/gripper_camera/image_raw/compressed',
			self.image_callback,
			10)
        self.save_dir = os.path.join(os.path.expanduser('~'), 'scan_images')
        os.makedirs(self.save_dir, exist_ok=True)
        self.get_logger().info(f"Scan images will be saved to {self.save_dir}")
        

    def execute_callback(self, goal_handle):
        # For testing purposes, we can disable the actual scanning and just return a dummy result
        if 1==0:
            self.get_logger().info('Received scan request, but scan server is currently disabled for testing.')
            goal_handle.abort()
            result = Scan.Result()
            result.success = False
            return result
        
        #Get goal parameters and start scan
        self.get_logger().info('Starting scan')
        feedback_msg = Scan.Feedback()
        goal = goal_handle.request
        self.get_logger().info(f"Received scan request for table {goal.table_id}, row {goal.row_id} at {goal.pose_id}")
        
        feedback_msg.current_state = f"Starting scan for table {goal.table_id}, row {goal.row_id} at {goal.pose_id}"
        goal_handle.publish_feedback(feedback_msg)
        
        #Error message if no image received yet
        if self.latest_image is None:

            self.get_logger().error("No image received yet")
            
            goal_handle.abort()

            result = Scan.Result()
            result.success = False
            feedback_msg.current_state = "Failed: No image received"
            goal_handle.publish_feedback(feedback_msg)
            return result
        
		#Create filepath
        filename = (f"{goal.table_id}_row{goal.row_id}{goal.pose_id}.jpg")
        filepath = os.path.join(self.save_dir, filename)
        
		#Save image
        cv2.imwrite(filepath, self.latest_image)
        self.get_logger().info(f"Saved scan image to {filepath}")
        feedback_msg.current_state = f"Scan saved to {filepath}"
        goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()
        result = Scan.Result()
        result.success = True
        result.image_path = filepath
        return result

    #Save image latest messages
    def image_callback(self, msg):
        try:
            # cv_image = self.bridge.compressed_imgmsg_to_cv2(msg, desired_encoding='bgr8')
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.latest_image = cv_image
            #self.get_logger().info(f'Received image from camera. Image shape: {cv_image.shape}')
            
        except Exception as e:
            self.get_logger().error(f'Error converting image: {e}')	
                  

def main(args=None):
    rclpy.init(args=args)

    scan_action_server = ScanActionServer()

    rclpy.spin(scan_action_server)


if __name__ == '__main__':
    main()