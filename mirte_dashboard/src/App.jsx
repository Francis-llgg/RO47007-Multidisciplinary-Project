import { useEffect, useMemo, useState, useRef } from "react";
import * as ROSLIB from "roslib";
import { Stage, Layer, Image, Rect, Line } from "react-konva";
import useImage from "use-image";
import "./App.css";

function quaternionToYaw(q) {
  const siny =
    2 * (q.w * q.z + q.x * q.y);

  const cosy =
    1 -
    2 * (q.y * q.y + q.z * q.z);

  return Math.atan2(siny, cosy);
}

export default function App() {
  const [connected, setConnected] = useState(false);
  const [cmdVelTopic, setCmdVelTopic] = useState(null);
  const [markers, setMarkers] = useState([]);
  const [map, setMap] = useState(null);
  const [robotPos, setRobotPos] = useState({
    x: 0,
    y: 0,
    yaw: 0,
  });

  useEffect(() => {
    const ros = new ROSLIB.Ros({
      url: "ws://localhost:9090",
    });

    ros.on("connection", () => {
      console.log("Connected");
      setConnected(true);
    });

    ros.on("close", () => {
      setConnected(false);
    });

    ros.on("error", (err) => {
      console.error(err);
    });

    // MAP
    const mapTopic = new ROSLIB.Topic({
      ros,
      name: "/map",
      messageType:
        "nav_msgs/OccupancyGrid",
    });

    mapTopic.subscribe((msg) => {
      setMap(msg);
    });

  // ODOM
  const odomTopic = new ROSLIB.Topic({
    ros,
    name: "/odom",
    messageType: "nav_msgs/Odometry",  
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

    // MOVEMENT
    const cmdTopic = new ROSLIB.Topic({
      ros,
      name:
        "/mirte_base_controller/cmd_vel_unstamped",
      messageType:
        "geometry_msgs/Twist",
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

  // Convert OccupancyGrid -> image
  const mapCanvas = useMemo(() => {
    if (!map) return null;

    const width = map.info.width;
    const height = map.info.height;

    const canvas =
      document.createElement("canvas");

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");

    const imageData =
      ctx.createImageData(width, height);

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const srcIndex =
          x + (height - y - 1) * width;

        const value =
          map.data[srcIndex];

        let color = 255;

        if (value === -1) {
          color = 180;
        } else {
          color =
            255 -
            (value / 100) * 255;
        }

        const idx =
          (y * width + x) * 4;

        imageData.data[idx] =
          color;
        imageData.data[idx + 1] =
          color;
        imageData.data[idx + 2] =
          color;
        imageData.data[idx + 3] =
          255;
      }
    }

    ctx.putImageData(imageData, 0, 0);

    return canvas.toDataURL();
  }, [map]);

  const [mapImage] = useImage(
    mapCanvas || ""
  );

  function worldToPixel(x, y) {
    if (!map) return { x: 0, y: 0 };

    const resolution =
      map.info.resolution;

    const origin =
      map.info.origin.position;

    const mapHeight =
      map.info.height;

    const px =
      (x - origin.x) /
      resolution;

    const py =
      mapHeight -
      (y - origin.y) /
        resolution;

    return {
      x: px,
      y: py,
    };
  }

  function pixelToWorld(px, py) {
    if (!map) return { x: 0, y: 0 };

    const resolution = map.info.resolution;
    const origin = map.info.origin.position;
    const mapHeight = map.info.height;

    return {
      x: px * resolution + origin.x,
      y: (mapHeight - py) * resolution + origin.y,
    };
  }

  const robotPixel = worldToPixel(
    robotPos.x,
    robotPos.y
  );

  return (
    <div className="app">
      <div className="mapContainer">
        {map && (
          <Stage
            width={map.info.width * 3}
            height={map.info.height * 3}
            draggable
          >
            <Layer>
              <Image
                image={mapImage}
                x={0}
                y={0}
                width={map.info.width * 3}
                height={map.info.height * 3}
              />
            </Layer>

            <Layer>
              <Rect
                x={robotPixel.x * 3}
                y={robotPixel.y * 3}
                width={30}
                height={20}
                offsetX={15}
                offsetY={10}
                rotation={-(robotPos.yaw * 180) / Math.PI}
                fill="blue"
              />
            </Layer>

            <Layer>
              <Line
                points={[robotPixel.x * 3, robotPixel.y * 3, robotPixel.x * 3 + Math.cos(robotPos.yaw) * 25, robotPixel.y * 3 - Math.sin(robotPos.yaw) * 25]}
                stroke="blue"
                strokeWidth={4}
              />
            </Layer>         
          </Stage>
        )}
      </div>

      <div className="controls">
        <button
          onMouseDown={() =>
            moveRobot(0.4, 0)
          }
          onMouseUp={() =>
            moveRobot(0, 0)
          }
        >
          ↑
        </button>

        <div className="middle">
          <button
            onMouseDown={() =>
              moveRobot(0, 1)
            }
            onMouseUp={() =>
              moveRobot(0, 0)
            }
          >
            ←
          </button>

          <button
            onClick={() =>
              moveRobot(0, 0)
            }
          >
            ■
          </button>

          <button
            onMouseDown={() =>
              moveRobot(0, -1)
            }
            onMouseUp={() =>
              moveRobot(0, 0)
            }
          >
            →
          </button>
        </div>

        <button
          onMouseDown={() =>
            moveRobot(-0.4, 0)
          }
          onMouseUp={() =>
            moveRobot(0, 0)
          }
        >
          ↓
        </button>
      </div>
    </div>
  );
}
