# Perception Dashboard Bridge

This ROS 2 package connects the saved perception snapshots to the dashboard UI.

It starts two components:

```text
1. HTTP server for saved PNG/JSON snapshots
2. latest_observation_publisher node
```

The dashboard subscribes to:

```text
/latest_observation
```

and receives the latest saved perception image URL plus the corresponding JSON metadata.

---

## What this package does

The full perception pipeline saves matched observation files:

```text
perception_snapshot_YYYYMMDD_HHMMSS.png
perception_snapshot_YYYYMMDD_HHMMSS.json
```

The PNG contains the saved perception image with overlays.

The JSON contains the matching metadata, such as:

```text
flower detections
flower length estimates
AprilTag scale information
greenhouse readings
timestamps
```

This package watches the snapshot folder and publishes the newest saved observation on:

```text
/latest_observation
```

Message type:

```text
std_msgs/msg/String
```

The message contains a JSON string like:

```json
{
  "image_path": "/home/user/ros2_ws/perception_snapshots/perception_snapshot_....png",
  "json_path": "/home/user/ros2_ws/perception_snapshots/perception_snapshot_....json",
  "image_url": "http://localhost:8088/perception_snapshot_....png",
  "json_url": "http://localhost:8088/perception_snapshot_....json",
  "metadata": {
    "flower_lengths": {},
    "greenhouse_reading": {}
  }
}
```

---

## Why the HTTP server is needed

A browser dashboard cannot directly open Linux file paths like:

```text
/home/user/ros2_ws/perception_snapshots/perception_snapshot_....png
```

Therefore, this package starts a local HTTP server on port `8088`.

The saved image becomes accessible as:

```text
http://localhost:8088/perception_snapshot_....png
```

The saved JSON becomes accessible as:

```text
http://localhost:8088/perception_snapshot_....json
```

If the dashboard runs on the same laptop as this bridge, `localhost` is correct.

If the dashboard runs on another device, launch this package with the laptop IP:

```text
base_url:=http://<LAPTOP_IP>:8088
```

---

## Package contents

Important files:

```text
perception_dashboard_bridge/
├── launch/
│   └── dashboard_bridge.launch.py
├── perception_dashboard_bridge/
│   ├── __init__.py
│   └── latest_observation_publisher.py
├── package.xml
├── setup.py
└── README.md
```

---

## Build

From the workspace root:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash

colcon build --symlink-install --packages-select perception_dashboard_bridge
source install/setup.bash
```

Check that the executable exists:

```bash
ros2 pkg executables perception_dashboard_bridge
```

Expected:

```text
perception_dashboard_bridge latest_observation_publisher
```

Check that the launch file is visible:

```bash
ros2 launch perception_dashboard_bridge dashboard_bridge.launch.py --show-args
```

Expected launch arguments:

```text
snapshot_dir
base_url
```

---

## Run the dashboard bridge

Start both the HTTP server and the latest observation publisher:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 launch perception_dashboard_bridge dashboard_bridge.launch.py
```

This starts:

```text
HTTP server on http://localhost:8088
/latest_observation publisher
```

Default snapshot folder:

```text
$HOME/ros2_ws/perception_snapshots
```

---

## Run with a custom snapshot folder

The `snapshot_dir` must match the folder used by the perception snapshot saver.

Example:

```bash
ros2 launch perception_dashboard_bridge dashboard_bridge.launch.py \
  snapshot_dir:=$HOME/Documents/Master_Robotics/Multi_Disciplinary_Project/perception_snapshots
```

If the dashboard runs on another device, also set `base_url`:

```bash
ros2 launch perception_dashboard_bridge dashboard_bridge.launch.py \
  snapshot_dir:=$HOME/Documents/Master_Robotics/Multi_Disciplinary_Project/perception_snapshots \
  base_url:=http://<LAPTOP_IP>:8088
```

---

## Full system usage

Run the full perception pipeline:

```bash
ros2 launch flower_detector mirte_full_perception.launch.py confidence:=0.30
```

Run the keyboard snapshot client:

```bash
ros2 run flower_detector keyboard_snapshot_client
```

Run the dashboard bridge:

```bash
ros2 launch perception_dashboard_bridge dashboard_bridge.launch.py
```

Press:

```text
s
```

in the keyboard snapshot client.

This creates a new PNG and JSON snapshot. The dashboard bridge detects the newest JSON file and publishes the observation on:

```text
/latest_observation
```

---

## Test

After pressing `s`, check:

```bash
ros2 topic echo /latest_observation --full-length
```

Expected output contains:

```text
image_url
json_url
metadata
```

Example image URL:

```text
http://localhost:8088/perception_snapshot_20260604_144824_249286.png
```

Open the URL in a browser. The saved perception image should appear.

You can also open the corresponding JSON by replacing `.png` with `.json`:

```text
http://localhost:8088/perception_snapshot_20260604_144824_249286.json
```

---

## Dashboard usage

The dashboard should subscribe to:

```text
/latest_observation
```

Message type:

```text
std_msgs/msg/String
```

The dashboard should parse `msg.data` as JSON.

Important fields:

```text
observation.image_url
observation.json_url
observation.metadata
observation.metadata.flower_lengths
observation.metadata.greenhouse_reading
```

The dashboard can display:

```text
latest saved perception image
flower count
flower class
confidence score
estimated flower length in pixels
estimated flower length in centimeters
AprilTag ID
temperature
humidity
CO2
light
soil moisture
```

---

## Final recommended terminal setup

Recommended demo setup:

```text
Terminal 1:
ros2 launch flower_detector mirte_full_perception.launch.py confidence:=0.30

Terminal 2:
ros2 run flower_detector keyboard_snapshot_client

Terminal 3:
ros2 launch perception_dashboard_bridge dashboard_bridge.launch.py
```

---

## Notes

This package does not run YOLO, AprilTag detection, greenhouse reading, or flower length estimation.

It only publishes the latest saved observation for the dashboard.

The data flow is:

```text
perception pipeline
        ↓
PNG + JSON saved locally
        ↓
perception_dashboard_bridge
        ↓
/latest_observation
        ↓
dashboard UI
```

The HTTP server must be running whenever the dashboard needs to open the `image_url` or `json_url`. The `dashboard_bridge.launch.py` file starts this server automatically.

---

## Add this package to GitLab

If this package is inside the main group repository:

```text
~/ros2_ws/src/mdp_mirte_master/perception_dashboard_bridge
```

commit it from the main repository root:

```bash
cd ~/ros2_ws/src/mdp_mirte_master

git status
git add perception_dashboard_bridge
git commit -m "Add perception dashboard bridge"
git push
```

Before pushing, check that generated folders are not included:

```bash
git status
```

Do not commit:

```text
build/
install/
log/
__pycache__/
*.pyc
```
