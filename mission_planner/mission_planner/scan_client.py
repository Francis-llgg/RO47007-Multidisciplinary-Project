import rclpy

from rclpy.action import ActionClient
from rclpy.node import Node

from mdp_interfaces.action import Scan
from std_srvs.srv import Trigger


class ScanClient(Node):

    def __init__(self, node):
        self.__node = node
        self._action_client = ActionClient(
            node,
            Scan,
            'scan'
        )

        self.client = self.__node.create_client(
            Trigger,
            '/save_perception_snapshot'
        )


    def call_snapshot_service(self):
        if not self.client.wait_for_service(timeout_sec=1.0):
            self.__node.get_logger().warn('Service /save_perception_snapshot is not available.')
            return

        request = Trigger.Request()
        future = self.client.call_async(request)
        future.add_done_callback(self.handle_response)

    def handle_response(self, future):
        try:
            response = future.result()
        except Exception as error:
            self.__node.get_logger().error(f'Snapshot service call failed: {error}')
            return

        if response.success:
            self.__node.get_logger().info(f'Snapshot saved: {response.message}')
        else:
            self.__node.get_logger().warn(f'Snapshot not saved: {response.message}')

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

        #Calling the snapshot service before performing the scan
        self.__node.get_logger().info("Saving perception snapshot before scan...")
        self.call_snapshot_service()

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