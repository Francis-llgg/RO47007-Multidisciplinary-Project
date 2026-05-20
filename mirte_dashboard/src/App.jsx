import { useEffect, useState } from "react";
import * as ROSLIB from "roslib";
import "./App.css";

export default function App() {
  const [connected, setConnected] = useState(false);
  const [frontLeftDistance, setFrontLeftDistance] =
    useState("waiting...");
  const [xPos, setXPos] = useState(0);
  const [yPos, setYPos] = useState(0);

  const [cmdVelTopic, setCmdVelTopic] = useState(null);

  useEffect(() => {
    const ros = new ROSLIB.Ros({
      url: "ws://localhost:9090",
    });

    ros.on("connection", () => {
      console.log("Connected to ROS");
      setConnected(true);
    });

    ros.on("error", (error) => {
      console.error("ROS error:", error);
    });

    ros.on("close", () => {
      console.log("Disconnected from ROS");
      setConnected(false);
    });

    // Distance sensor topic
    const distanceTopic = new ROSLIB.Topic({
      ros: ros,
      name: "/mirte/distance/front_left",
      messageType: "sensor_msgs/msg/Range",
    });

    distanceTopic.subscribe((message) => {
      setFrontLeftDistance(
        message.range.toFixed(2)
      );
    });

    // Robot position topic
    const odomTopic = new ROSLIB.Topic({
      ros: ros,
      name: "/odom",
      messageType: "nav_msgs/msg/Odometry",
    });

    odomTopic.subscribe((message) => {
      setXPos(
        message.pose.pose.position.x.toFixed(2)
      );
      setYPos(
        message.pose.pose.position.y.toFixed(2)
      );
    });

    // Movement topic
    const cmdTopic = new ROSLIB.Topic({
      ros: ros,
      name: "/mirte_base_controller/cmd_vel_unstamped",
      messageType: "geometry_msgs/msg/Twist",
    });

    setCmdVelTopic(cmdTopic);

    return () => {
      distanceTopic.unsubscribe();
      odomTopic.unsubscribe();
      ros.close();
    };
  }, []);

  function moveRobot(linearX, angularZ) {
    if (!cmdVelTopic) return;

    const twist = {
      linear: {
        x: linearX,
        y: 0,
        z: 0,
      },
      angular: {
        x: 0,
        y: 0,
        z: angularZ,
      },
    };

    cmdVelTopic.publish(twist);

    console.log("Sent command:", twist);
  }

  return (
    <div className="dashboard">
      <h1>MIRTE Dashboard</h1>

      <h2>
        Status:{" "}
        {connected
          ? "🟢 Connected"
          : "🔴 Disconnected"}
      </h2>

      <div className="card">
        <h3>Distance Sensor</h3>
        <p>
          Front Left Distance:{" "}
          {frontLeftDistance} m
        </p>
      </div>

      <div className="card">
        <h3>Robot Position</h3>
        <p>X: {xPos}</p>
        <p>Y: {yPos}</p>
      </div>

      <div className="card">
        <h3>Movement Controls</h3>

        <div className="controls">
          <button
            onClick={() => moveRobot(0.5, 0)}
          >
            ↑
          </button>

          <div>
            <button
              onClick={() => moveRobot(0, 1)}
            >
              ←
            </button>

            <button
              onClick={() => moveRobot(0, 0)}
            >
              ■
            </button>

            <button
              onClick={() => moveRobot(0, -1)}
            >
              →
            </button>
          </div>

          <button
            onClick={() => moveRobot(-0.5, 0)}
          >
            ↓
          </button>
        </div>
      </div>
    </div>
  );
}
