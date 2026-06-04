import rclpy

from rclpy.action import ActionClient
from rclpy.node import Node

from mdp_interfaces.action import Scan

class ScanClient(Node):

    def __init__(self, node):
        self.__node = node
        self._action_client = ActionClient(
            node,
            Scan,
            'scan'
        )

    def perform_scan(self, table_id, row_id, pose_id):

        self.__node.get_logger().info("Waiting for scan server...")

        self._action_client.wait_for_server()

        goal_msg = Scan.Goal()

        goal_msg.table_id = str(table_id)
        goal_msg.row_id = str(row_id)
        goal_msg.pose_id = str(pose_id)

        self.__node.get_logger().info(
            f"Sending scan request: "
            f"{table_id} {row_id} {pose_id}"
        )

        future = self._action_client.send_goal_async(
            goal_msg
        )

        rclpy.spin_until_future_complete(self.__node, future)

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.__node.get_logger().error(
                "Scan goal rejected"
            )

            return None

        self.__node.get_logger().info(
            "Scan goal accepted"
        )

		
        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self.__node,
            result_future
        )

        result = result_future.result().result

        return result