import { useEffect, useState } from 'react';
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

  const [cmdVelTopic, setCmdVelTopic] = useState(null);

  useEffect(() => {
    const ros = new ROSLIB.Ros({
      url: 'ws://localhost:9090',
    });

    ros.on('connection', () => {
      console.log('Connected to ROS');
      setConnected(true);
    });

    ros.on('close', () => {
      setConnected(false);
    });

    ros.on('error', console.error);

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

    const cmdTopic = new ROSLIB.Topic({
      ros,
      name: '/mirte_base_controller/cmd_vel_unstamped',
      messageType: 'geometry_msgs/Twist',
    });

    setCmdVelTopic(cmdTopic);

    return () => {
      mapTopic.unsubscribe();
      odomTopic.unsubscribe();
      ros.close();
    };
  }, []);

  function moveRobot(linearX, angularZ) {
    if (!cmdVelTopic) return;

    cmdVelTopic.publish({
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

  return {
    connected,
    map,
    robotPos,
    moveRobot,
  };
}
