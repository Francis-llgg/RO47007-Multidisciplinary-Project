#!/usr/bin/env python3
"""
Reads the ROS /map topic, detects table clusters via BFS,
and generates a tables.yaml for the mission_planner package.
"""

import rclpy
import math
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
import yaml
import os
from collections import deque


class MissionGenerator(Node):

    def __init__(self):
        super().__init__('mission_generator')

        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )

        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            qos
        )

        self.done = False
        self.get_logger().info("Waiting for map...")

    def map_callback(self, msg):

        if self.done:
            return
        self.done = True

        width = msg.info.width
        height = msg.info.height
        res = msg.info.resolution
        self.get_logger().info(f"Map resolution = {res:.3f} m/cell")
        ox = msg.info.origin.position.x
        oy = msg.info.origin.position.y

        visited = [False] * (width * height)
        clusters = []

        for y in range(height):
            for x in range(width):

                idx = y * width + x
                val = msg.data[idx]

                if visited[idx]:
                    continue
                if val != 100:
                    continue

                # BFS
                cluster = []
                q = deque([idx])
                visited[idx] = True

                while q:
                    curr = q.popleft()
                    cluster.append(curr)

                    cx, cy = curr % width, curr // width

                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                        nx, ny = cx + dx, cy + dy

                        if 0 <= nx < width and 0 <= ny < height:
                            nidx = ny * width + nx

                            if not visited[nidx] and msg.data[nidx] == 100:
                                visited[nidx] = True
                                q.append(nidx)
                
                self.get_logger().info(
                         f"cluster size={len(cluster)} ")
                # filter cluster size
                if not (40 <= len(cluster) <= 200):
                    continue

                xs = [c % width for c in cluster]
                ys = [c // width for c in cluster]

                bbox_w = max(xs) - min(xs)
                bbox_h = max(ys) - min(ys)

                self.get_logger().info(f"bbox_w={bbox_w} cells ({bbox_w * res:.2f} m), "f"bbox_h={bbox_h} cells ({bbox_h * res:.2f} m)")

                aspect = max(bbox_w, bbox_h) / (min(bbox_w, bbox_h) + 1e-6)

                #if aspect > 20:
                 #   continue

                sx = sum(xs) / len(xs)
                sy = sum(ys) / len(ys)

                cx = ox + sx * res
                cy = oy + sy * res

                # remove robot start noise
                if math.hypot(cx - ox, cy - oy) < 0.8:
                    continue

                orientation = "vertical" if bbox_h > bbox_w else "horizontal"
                self.get_logger().info(
                           f"ACCEPTED bbox_w={bbox_w} bbox_h={bbox_h}"
                )
                clusters.append({
                    "cx": cx,
                    "cy": cy,
                    "orientation": orientation,
                    "bbox_w": bbox_w,
                    "bbox_h": bbox_h
                })

                self.get_logger().info(
                    f"Table at [{cx:.2f}, {cy:.2f}] orientation={orientation}"
                )

        self.get_logger().info(f"Detected {len(clusters)} tables")

        self.generate_yaml(clusters)

        rclpy.shutdown()

    def generate_yaml(self, clusters):

        tables = []

        row_offset = 0.5
        step = 0.3

        def valid_pose(p):
            x, y, _ = p["pose"]
            return 0.3 < x < 4.7 and 0.3 < y < 9.7

        for i, table in enumerate(clusters):

            cx = table["cx"]
            cy = table["cy"]
            orientation = table["orientation"]
            bbox_w = table["bbox_w"]
            bbox_h = table["bbox_h"]

            self.get_logger().info(
                     f"T{i+1}: bbox_w={bbox_w}, bbox_h={bbox_h}, "
                     f"orientation={orientation}"
            )

            table_id = f"T{i+1}"

            if orientation == "vertical":

                row_A_x = cx - row_offset
                row_B_x = cx + row_offset

                scan_points_A = [
                    {"name": "pose_1", "pose": [round(row_A_x, 3), round(cy - step, 3), 0.0]},
                    {"name": "pose_2", "pose": [round(row_A_x, 3), round(cy, 3), 0.0]},
                    {"name": "pose_3", "pose": [round(row_A_x, 3), round(cy + step, 3), 0.0]},
                ]

                scan_points_B = [
                    {"name": "pose_1", "pose": [round(row_B_x, 3), round(cy - step, 3), 0.0]},
                    {"name": "pose_2", "pose": [round(row_B_x, 3), round(cy, 3), 0.0]},
                    {"name": "pose_3", "pose": [round(row_B_x, 3), round(cy + step, 3), 0.0]},
                ]

            else:

                row_A_y = cy - row_offset
                row_B_y = cy + row_offset

                scan_points_A = [
                    {"name": "pose_1", "pose": [round(cx - step, 3), round(row_A_y, 3), 0.0]},
                    {"name": "pose_2", "pose": [round(cx, 3), round(row_A_y, 3), 0.0]},
                    {"name": "pose_3", "pose": [round(cx + step, 3), round(row_A_y, 3), 0.0]},
                ]

                scan_points_B = [
                    {"name": "pose_1", "pose": [round(cx - step, 3), round(row_B_y, 3), 0.0]},
                    {"name": "pose_2", "pose": [round(cx, 3), round(row_B_y, 3), 0.0]},
                    {"name": "pose_3", "pose": [round(cx + step, 3), round(row_B_y, 3), 0.0]},
                ]

            scan_points_A = [p for p in scan_points_A if valid_pose(p)]
            scan_points_B = [p for p in scan_points_B if valid_pose(p)]

            tables.append({
                "table_id": table_id,
                "status": "pending",
                "rows": [
                    {
                        "row_id": "A",
                        "status": "pending",
                        "scan_points": scan_points_A
                    },
                    {
                        "row_id": "B",
                        "status": "pending",
                        "scan_points": scan_points_B
                    }
                ]
            })

        output = {"tables": tables}

        out_path = os.path.expanduser(
            "~/proj_ws/src/mdp_mirte_master/mission_planner/config/tables_generated.yaml"
        )

        with open(out_path, "w") as f:
            yaml.dump(output, f, default_flow_style=False, sort_keys=False)

        self.get_logger().info(f"Saved tables to {out_path}")


def main():
    rclpy.init()
    node = MissionGenerator()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
