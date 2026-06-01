import rclpy
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from tf_transformations import quaternion_from_euler


class NavigationClient:
    def __init__(self, node):
        self._node = node

        self._client = ActionClient(node, NavigateToPose, 'navigate_to_pose')

        self._node.get_logger().info("Waiting for Nav2 action server...")
        self._client.wait_for_server()
        self._node.get_logger().info("Nav2 action server ready.")

    def navigate_to(self, pose):
        """
        pose = (x, y, yaw)
        """
        self._node.get_logger().info(f"Navigating to pose: {pose}, type of pose: {type(pose)}")
        goal = NavigateToPose.Goal()

        pose_msg = PoseStamped()
        pose_msg.header.frame_id = "map"
        pose_msg.header.stamp = self._node.get_clock().now().to_msg()

        pose_msg.pose.position.x = float(pose[0])
        pose_msg.pose.position.y = float(pose[1])
        pose_msg.pose.position.z = 0.0

        qx, qy, qz, qw = quaternion_from_euler(0.0, 0.0, pose[2])
        pose_msg.pose.orientation.x = qx
        pose_msg.pose.orientation.y = qy
        pose_msg.pose.orientation.z = qz
        pose_msg.pose.orientation.w = qw

        goal.pose = pose_msg

        self._node.get_logger().info(f"Sending goal: {pose}")

        send_future = self._client.send_goal_async(goal, feedback_callback=self._feedback_cb)

        rclpy.spin_until_future_complete(self._node, send_future)

        goal_handle = send_future.result()

        if not goal_handle.accepted:
            self._node.get_logger().error("Goal rejected")
            return False

        self._node.get_logger().info("Goal accepted")

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(self._node, result_future)

        result = result_future.result().result

        return True

    def _feedback_cb(self, feedback_msg):
        feedback = feedback_msg.feedback
        self._node.get_logger().info(
            f"Distance remaining: {feedback.distance_remaining:.2f}"
        )