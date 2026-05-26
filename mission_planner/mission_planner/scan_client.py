import rclpy

from rclpy.action import ActionClient
from rclpy.node import Node

from mission_planner.action import Scan

class ScanClient(Node):

    def __init__(self):

        super().__init__('scan_client')

        self._action_client = ActionClient(
            self,
            Scan,
            'scan'
        )

    def perform_scan(self, table_id, row_id, pose_id):

        self.get_logger().info("Waiting for scan server...")

        self._action_client.wait_for_server()

        goal_msg = Scan.Goal()

        goal_msg.table_id = table_id
        goal_msg.row_id = row_id
        goal_msg.pose_id = pose_id

        self.get_logger().info(
            f"Sending scan request: "
            f"{table_id} {row_id} {pose_id}"
        )

        future = self._action_client.send_goal_async(
            goal_msg
        )

        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().error(
                "Scan goal rejected"
            )

            return None

        self.get_logger().info(
            "Scan goal accepted"
        )

		
        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future
        )

        result = result_future.result().result

        return result