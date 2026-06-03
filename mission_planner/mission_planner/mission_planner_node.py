from mission_planner.mission_data import MissionDatabase
from mission_planner.navigation_client import NavigationClient
from mission_planner.scan_client import ScanClient
import rclpy
from rclpy.node import Node
from pprint import pprint

class MissionPlannerNode(Node):

    def __init__(self):
        super().__init__('mission_planner')
        self.get_logger().info("Mission Planner Node started")

        self.db = MissionDatabase("config/tables.yaml", self)
        self.nav_client = NavigationClient(self)
        self.scan_client = ScanClient(self)

    def run(self):
        self.pending_rows = self.db.get_pending_rows()
        self.get_logger().info(f"Pending tasks: {pprint(self.pending_rows)}")
        for row in self.pending_rows:
            self.get_logger().info(f"Executing task for table {row['table_id']} row {row['row_id']} with scan points: {row['scan_points']}")
            self.db.execute_row(
                row, 
                navigation_client=self.nav_client, 
                scan_client=self.scan_client
            )

def main():
    rclpy.init()
    node = MissionPlannerNode()
    node.run()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()