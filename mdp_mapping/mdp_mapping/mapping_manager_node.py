#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry, OccupancyGrid
from std_srvs.srv import Trigger
from mdp_mapping.map_filter import filter_map_pgm, write_filtered_yaml


class MappingManagerNode(Node):

    def __init__(self):
        super().__init__("mapping_manager_node")

        self.declare_parameter("map_save_dir", "")
        self.declare_parameter("map_name", "greenhouse_map")
        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("odom_topic", "/odom")
        self.declare_parameter("map_topic", "/map")

        self.declare_parameter("enable_filtering", True)
        self.declare_parameter("min_obstacle_area", 8)
        self.declare_parameter("filter_kernel_size", 3)

        self.map_save_dir = self.get_parameter("map_save_dir").value
        self.map_name = self.get_parameter("map_name").value
        self.enable_filtering = self.get_parameter("enable_filtering").value
        self.min_obstacle_area = self.get_parameter("min_obstacle_area").value
        self.filter_kernel_size = self.get_parameter("filter_kernel_size").value

        self.scan_received = False
        self.odom_received = False
        self.map_received = False

        scan_topic = self.get_parameter("scan_topic").value
        odom_topic = self.get_parameter("odom_topic").value
        map_topic = self.get_parameter("map_topic").value
        

        self.create_subscription(
            LaserScan,
            scan_topic,
            self.scan_callback,
            10,
        )

        self.create_subscription(
            Odometry,
            odom_topic,
            self.odom_callback,
            10,
        )

        self.create_subscription(
            OccupancyGrid,
            map_topic,
            self.map_callback,
            10,
        )

        self.save_map_service = self.create_service(
            Trigger,
            "save_map",
            self.save_map_callback,
        )

        self.timer = self.create_timer(5.0, self.status_timer_callback)

        self.get_logger().info("Mapping manager node started.")
        self.get_logger().info(f"Monitoring scan topic: {scan_topic}")
        self.get_logger().info(f"Monitoring odom topic: {odom_topic}")
        self.get_logger().info(f"Monitoring map topic: {map_topic}")
        self.get_logger().info("Use this command to save the map:")
        self.get_logger().info("ros2 service call /save_map std_srvs/srv/Trigger {}")

    def scan_callback(self, msg: LaserScan):
        self.scan_received = True

    def odom_callback(self, msg: Odometry):
        self.odom_received = True

    def map_callback(self, msg: OccupancyGrid):
        self.map_received = True

    def status_timer_callback(self):
        self.get_logger().info(
            f"Mapping status | /scan: {self.scan_received}, "
            f"/odom: {self.odom_received}, /map: {self.map_received}"
        )

        if not self.scan_received:
            self.get_logger().warn("No /scan data received yet.")

        if not self.odom_received:
            self.get_logger().warn("No /odom data received yet.")

        if not self.map_received:
            self.get_logger().warn("No /map data received yet. Check slam_toolbox and TF.")

    def save_map_callback(self, request, response):
        if not self.map_received:
            response.success = False
            response.message = "Cannot save map because /map has not been received yet."
            self.get_logger().error(response.message)
            return response

        if self.map_save_dir == "":
            # Default runtime map directory:
            # ~/ros2_ws/maps/mdp_mapping
            home_dir = os.path.expanduser("~")
            self.map_save_dir = os.path.join(
                home_dir,
                "ros2_ws",
                "maps"
            )

        posegraph_dir = os.path.join(self.map_save_dir, "posegraph")
        raw_map_dir = os.path.join(self.map_save_dir, "raw")
        filtered_map_dir = os.path.join(self.map_save_dir, "filtered")

        os.makedirs(posegraph_dir, exist_ok=True)
        os.makedirs(raw_map_dir, exist_ok=True)
        os.makedirs(filtered_map_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_base_name = f"{self.map_name}_{timestamp}"

        raw_map_base_path = os.path.join(
            raw_map_dir,
            f"{map_base_name}_raw"
        )

        command = [
            "ros2",
            "run",
            "nav2_map_server",
            "map_saver_cli",
            "-f",
            raw_map_base_path,
            "--ros-args",
            "-p",
            "map_subscribe_transient_local:=true",
        ]

        self.get_logger().info(
            f"Saving raw map to: {raw_map_base_path}.yaml / .pgm"
        )

        try:
            # save posegraph and map sequentially to avoid slam_toolbox serialize_map service conflicts with map_saver_cli
            posegraph_base_path = os.path.join(
                posegraph_dir,
                map_base_name
            )

            serialize_command = [
                "ros2",
                "service",
                "call",
                "/slam_toolbox/serialize_map",
                "slam_toolbox/srv/SerializePoseGraph",
                f"{{filename: '{posegraph_base_path}'}}",
            ]

            self.get_logger().info(
                f"Saving slam_toolbox posegraph to: {posegraph_base_path}"
            )

            serialize_result = subprocess.run(
                serialize_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
            )

            if serialize_result.returncode != 0:
                response.success = False
                response.message = f"Posegraph saving failed: {serialize_result.stderr}"
                self.get_logger().error(response.message)
                return response

            self.get_logger().info(
                f"Posegraph saved successfully: {posegraph_base_path}"
            )


            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=20,
            )

            if result.returncode != 0:
                response.success = False
                response.message = f"Map saving failed: {result.stderr}"
                self.get_logger().error(response.message)
                return response

            raw_pgm_path = raw_map_base_path + ".pgm"
            raw_yaml_path = raw_map_base_path + ".yaml"

            self.get_logger().info(f"Raw map saved successfully: {raw_yaml_path}")

            if not self.enable_filtering:
                response.success = True
                response.message = (
                    "Posegraph and raw map saved successfully. Filtering disabled.\n"
                    f"Posegraph base path: {posegraph_base_path}\n"
                    f"Raw map: {raw_yaml_path}"
                )
                return response

            filtered_map_base_path = os.path.join(
                filtered_map_dir,
                f"{map_base_name}_filtered"
            )

            filtered_pgm_path = filtered_map_base_path + ".pgm"
            filtered_yaml_path = filtered_map_base_path + ".yaml"

            filter_map_pgm(
                input_pgm=raw_pgm_path,
                output_pgm=filtered_pgm_path,
                min_obstacle_area=int(self.min_obstacle_area),
                kernel_size=int(self.filter_kernel_size),
            )

            write_filtered_yaml(
                raw_yaml_path=raw_yaml_path,
                filtered_yaml_path=filtered_yaml_path,
                filtered_pgm_path=filtered_pgm_path,
            )

            response.success = True
            response.message = (
                "Posegraph, raw map, and filtered map saved successfully.\n"
                f"Posegraph base path: {posegraph_base_path}\n"
                f"Raw map: {raw_yaml_path}\n"
                f"Filtered map: {filtered_yaml_path}"
            )

            self.get_logger().info(response.message)

        except subprocess.TimeoutExpired:
            response.success = False
            response.message = "Map saving timed out."
            self.get_logger().error(response.message)

        except Exception as e:
            response.success = False
            response.message = f"Map saving/filtering error: {str(e)}"
            self.get_logger().error(response.message)

        return response

def main(args=None):
    rclpy.init(args=args)
    node = MappingManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()