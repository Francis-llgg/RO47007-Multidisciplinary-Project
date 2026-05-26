from MissionData import MissionDatabase
import pprint
from Navigation_Client import NavigationClient
from scan_client import ScanClient
import rclpy

if __name__ == "__main__":
    db = MissionDatabase("tables.yaml")
    pending_rows = db.get_pending_rows()
    pprint(pending_rows)
    
    rclpy.init()
    nav = NavigationClient()
    scan_client = ScanClient()
    
    for row in pending_rows:
        print(f"Executing task for table {row['table_id']} row {row['row']} with scan points: {row['scan_points']}")
        db.execute_row(row, navigation_client=nav, scan_client=scan_client)