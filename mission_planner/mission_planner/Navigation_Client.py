import rclpy

from tf_transformations import quaternion_from_euler
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import (
    BasicNavigator,
    TaskResult
)


class NavigationClient:

    def __init__(self):

        self.navigator = BasicNavigator()

        print("Waiting for Nav2 to become active...")
        self.navigator.waitUntilNav2Active()
        print("Nav2 is active!")

    def navigate_to(self, pose):

        goal_pose = PoseStamped()

        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = (
            self.navigator.get_clock().now().to_msg()
        )

        goal_pose.pose.position.x = float(pose[0])
        goal_pose.pose.position.y = float(pose[1])
        goal_pose.pose.position.z = 0.0

        # Simple orientation for now
        qx, qy, qz, qw = quaternion_from_euler(0, 0, pose[2])

        goal_pose.pose.orientation.x = qx
        goal_pose.pose.orientation.y = qy
        goal_pose.pose.orientation.z = qz
        goal_pose.pose.orientation.w = qw

        print(f"Navigating to: {pose}")

        self.navigator.goToPose(goal_pose)

        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()

            result = self.navigator.getResult()

            if result == TaskResult.SUCCEEDED:
                print("Arrived successfully!")
                return True

            elif result == TaskResult.FAILED:
                print("Navigation failed!")
                return False

            elif result == TaskResult.CANCELED:
                print("Navigation canceled!")
                return False

        return False