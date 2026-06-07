import { useEffect, useState, useRef } from 'react';
import * as ROSLIB from 'roslib';
import { quaternionToYaw } from './math';

export default function useROS() {
  const [connected, setConnected] = useState(false);
  const [map, setMap] = useState(null);
  const [robotPos, setRobotPos] = useState({
    x: 0,
    y: 0,
    yaw: 0,
  });
  const [battery, setBattery] = useState({
    percentage: 0,
  })
  const [cameraImage, setCameraImage] = useState(null);
  const cmdVelTopic = useRef(null);
  const armTopic = useRef(null);
  const initialPoseTopic = useRef(null);

  useEffect(() => {
    const rosUrl = import.meta.env.VITE_ROS_URL;
    const ros = new ROSLIB.Ros({
      url: rosUrl,
    });

    ros.on('connection', () => {
      console.log('Connected to ROS');
      setConnected(true);
    });

    ros.on('close', () => {
      setConnected(false);
    });

    ros.on('error', console.error);

    const batteryTopic = new ROSLIB.Topic({
      ros,
      name: '/io/power/power_watcher',
      messageType: 'sensor_msgs/BatteryState',
    });

    batteryTopic.subscribe((msg) => {
      setBattery({
        percentage: msg.percentage * 100
      });
    });

    const mapTopic = new ROSLIB.Topic({
      ros,
      name: '/map',
      messageType: 'nav_msgs/OccupancyGrid',
    });

    mapTopic.subscribe(setMap);

    const odomTopic = new ROSLIB.Topic({
      ros,
      name: '/odom',
      messageType: 'nav_msgs/Odometry',
    });

    odomTopic.subscribe((msg) => {
      setRobotPos({
        x: msg.pose.pose.position.x,
        y: msg.pose.pose.position.y,
        yaw: quaternionToYaw(
          msg.pose.pose.orientation
        ),
      });
    });

    const cmdVelName = import.meta.env.VITE_CMD_TOPIC;
    cmdVelTopic.current = new ROSLIB.Topic({
      ros,
      name: cmdVelName,
      messageType: 'geometry_msgs/Twist',
    });

    const cameraTopic = new ROSLIB.Topic({
      ros,
      name: '/gripper_camera/image_raw/compressed',
      messageType: 'sensor_msgs/CompressedImage',
    });

    cameraTopic.subscribe((msg) => {
      setCameraImage(
        `data:image/jpeg;base64,${msg.data}`
      );
    });

    armTopic.current = new ROSLIB.Topic({
      ros,
      name: "/mirte_master_arm_controller/joint_trajectory",
      messageType: "trajectory_msgs/JointTrajectory",
    });

    initialPoseTopic.current = new ROSLIB.Topic({
      ros,
      name: "/initialpose",
      messageType: "geometry_msgs/PoseWithCovarianceStamped",
    });

    return () => {
      batteryTopic.unsubscribe();
      mapTopic.unsubscribe();
      odomTopic.unsubscribe();
      cameraTopic.unsubscribe();
      ros.close();
    };
  }, []);

  function moveRobot(linearX, angularZ) {
    console.log("moveRobot CALLED", linearX, angularZ);
    if (!cmdVelTopic.current) {console.log("CMD VEL NOT READY"); return;}

    cmdVelTopic.current.publish({
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
    });
  }

  function sendArmPose(positions) {
    if (!armTopic.current) return;

    const msg = {
      joint_names: [
        "shoulder_pan_joint",
        "shoulder_lift_joint",
        "elbow_joint",
        "wrist_joint",
      ],
      points: [
        {
          positions: positions,
          time_from_start: {
            sec: 3,
            nanosec: 0,
          },
        },
      ],
    };

    armTopic.current.publish(msg);
  }

  function setInitialPose(x, y, yaw) {
    if (!initialPoseTopic.current) return;

    const qz = Math.sin(yaw / 2);
    const qw = Math.cos(yaw / 2);

    initialPoseTopic.current.publish({
      header: {
        frame_id: "map",
      },
      pose: {
        pose: {
          position: {
            x,
            y,
            z: 0,
          },
          orientation: {
            x: 0,
            y: 0,
            z: qz,
            w: qw,
          },
        },
        covariance: [
          0.25,0,0,0,0,0,
          0,0.25,0,0,0,0,
          0,0,0,0,0,0,
          0,0,0,0,0,0,
          0,0,0,0,0,0,
          0,0,0,0,0,0.0685,
        ],
      },
    });
  }

  return {
    connected,
    map,
    robotPos,
    moveRobot,
    battery,
    cameraImage,
    sendArmPose,
    setInitialPose,
  };
}

