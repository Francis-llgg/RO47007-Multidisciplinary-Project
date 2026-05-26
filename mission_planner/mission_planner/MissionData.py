import yaml
import os
from pprint import pprint


class MissionDatabase:

    def __init__(self, path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(base_dir, path)
        self.data = self.load()

    def load(self):
        try:
            with open(self.path, "r") as file:
                return yaml.safe_load(file) or {"tables": []}
        except FileNotFoundError:
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
        for pose in task.get("scan_points", []):
            
            success = navigation_client.navigate_to(pose)
            if not success:
                print(f"Failed to navigate to {pose}, skipping scan.")
                return False

            success = scan_client.perform_scan(pose, task.get("table_id"), )
            if not success:
                print(f"Failed to perform scan at {pose}, skipping to next point.")
                return False

        self.mark_completed(table_id=task.get("table_id"), row_id=task.get("row"))
        print(f"Completed task for table {task.get('table_id')} row {task.get('row')}.")