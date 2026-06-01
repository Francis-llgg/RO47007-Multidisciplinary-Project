import yaml
from ament_index_python.packages import get_package_share_directory
import os
from pprint import pprint


class MissionDatabase:

    def __init__(self, path, node):
        self._node = node
        
        base_dir = get_package_share_directory("mission_planner")
        self.path = os.path.join(base_dir, path)
        self.data = self.load()
        

    def load(self):
        try:
            with open(self.path, "r") as file:
                self._node.get_logger().info(f"Loading mission data from {self.path}")
                return yaml.safe_load(file) or {"tables": []}
        except FileNotFoundError:
            self._node.get_logger().error(f"Mission data file not found at {self.path}. Starting with empty database.")
            return {"Note": "No tables found. Please add tables to the YAML file."}

    def save(self):
        with open(self.path, "w") as file:
            yaml.dump(self.data, file)

    def get_pending_rows(self):
        pending = []
        for table in self.data.get("tables", []):
            if table.get("status") != "completed":
                for row in table.get("rows", []):
                    if row.get("status") != "completed":
                        pending.append({
                            "table_id": table.get("table_id"),
                            "row": row.get("row_id"),
                            "scan_points": row.get("scan_points")
                        })
        return pending

    def mark_completed(self, table_id=None, row_id=None):
        for table in self.data.get("tables", []):
            if table_id == table.get("table_id"):
                for row in table.get("rows", []):
                    if row.get("row_id") == row_id:
                        row["status"] = "completed"

            if all(r.get("status") == "completed" for r in table.get("rows", [])):
                table["status"] = "completed"

        self.save()

    def execute_row(self, task, navigation_client, scan_client):
        for point in task.get("scan_points", []):
            pose = point["pose"]
            success = navigation_client.navigate_to(pose)
            if not success:
                self._node.get_logger().error(f"Failed to navigate to {pose}, skipping scan.")
                return False

            success = scan_client.perform_scan(pose, task.get("table_id"), )
            if not success:
                self._node.get_logger().error(f"Failed to perform scan at {point}, skipping to next point.")
                return False

        self.mark_completed(table_id=task.get("table_id"), row_id=task.get("row"))
        self._node.get_logger().info(f"Completed task for table {task.get('table_id')} row {task.get('row')}.")