# MIRTE Full Perception Pipeline — Quick Run Guide

This README contains the concise steps to run the current MIRTE perception pipeline.

## What it runs

The full launch starts:

```text
greenhouse_bridge
compressed_to_raw_republisher
AprilTag detector
YOLO flower detector
combined_visualizer
greenhouse_tag_reader
perception_snapshot_saver
flower_length_estimator
```

The keyboard snapshot client is run separately so it can read keypresses reliably.

Main outputs:

```text
/perception/image_combined
/flower_detector/detections
/gripper_camera/tags
/greenhouse/tag_reading
/flower_detector/flower_lengths
/save_perception_snapshot
```

---

## Build after code changes

Run on the laptop:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select flower_detector
source install/setup.bash
```

Check custom executables:

```bash
ros2 pkg executables flower_detector | grep -E "greenhouse|snapshot|keyboard|length"
```

Expected:

```text
flower_detector greenhouse_tag_reader
flower_detector perception_snapshot_saver
flower_detector keyboard_snapshot_client
flower_detector flower_length_estimator
```

---

## 1. MIRTE terminal — check camera

Run on MIRTE:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

ros2 topic list | grep gripper_camera
ros2 topic hz /gripper_camera/image_raw
```

Expected:

```text
/gripper_camera/image_raw
/gripper_camera/image_raw/compressed
around 30 Hz
```

Stop the rate check with `Ctrl+C`.

---

## 2. Laptop terminal — check MIRTE topics

Run on the laptop:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 daemon stop
ros2 daemon start

ros2 topic list | grep gripper_camera
ros2 topic hz /gripper_camera/image_raw/compressed
```

Expected compressed rate:

```text
15–30 Hz
```

Stop with `Ctrl+C`.

---

## 3. Laptop terminal — start full pipeline

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 launch flower_detector mirte_full_perception.launch.py confidence:=0.30
```

Check nodes:

```bash
ros2 node list | grep -E "greenhouse|snapshot|length|yolo|combined|republisher"
```

Expected nodes include:

```text
/greenhouse_bridge
/greenhouse_tag_reader
/perception_snapshot_saver
/flower_length_estimator
/yolo_flower_detector
/combined_visualizer
/compressed_to_raw_republisher
```

---

## 4. Laptop terminal — keyboard snapshot client

Run separately:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 run flower_detector keyboard_snapshot_client
```

Press:

```text
s
```

to save a snapshot.

Press:

```text
q
```

to quit.

Saved files:

```text
~/ros2_ws/perception_snapshots/
```

Each snapshot creates:

```text
perception_snapshot_YYYYMMDD_HHMMSS.png
perception_snapshot_YYYYMMDD_HHMMSS.json
```

---

## 5. Laptop terminal — view output

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 run rqt_image_view rqt_image_view
```

Select:

```text
/perception/image_combined
```

Expected result:

```text
MIRTE camera image + YOLO boxes + AprilTag overlay
```

---

## Useful test commands

### YOLO detections

```bash
ros2 topic echo /flower_detector/detections
```

Expected when a flower is visible:

```text
class_id: tulip_red
score: ...
bbox:
  size_x: ...
  size_y: ...
```

### AprilTag detections

```bash
ros2 topic echo /gripper_camera/tags
```

Expected when an AprilTag is visible:

```text
detections:
- id: ...
  centre:
    x: ...
    y: ...
```

### Greenhouse readings

```bash
ros2 topic echo /greenhouse/tag_reading --full-length
```

Expected:

```json
{
  "tag_id": "7",
  "readings": [
    {"name": "temperature", "value": 13.18},
    {"name": "humidity", "value": 46.52},
    {"name": "soil_moisture", "value": 0.42}
  ]
}
```

### Flower length estimation

```bash
ros2 topic echo /flower_detector/flower_lengths --full-length
```

Expected:

```json
{
  "flower_count": 1,
  "scale": {
    "scale_source": "apriltag",
    "cm_per_pixel": 0.24,
    "tag_size_cm": 5.0,
    "last_tag_id": 7
  },
  "flowers": [
    {
      "class_id": "tulip_red",
      "estimated_length_px": 231.3,
      "estimated_length_cm": 55.6
    }
  ]
}
```

---

## Length estimation method

The flower height in pixels is the YOLO bounding-box height:

```text
estimated_length_px = bbox.size_y
```

The AprilTag is used as a visual ruler:

```text
cm_per_pixel = tag_size_cm / tag_height_px
estimated_length_cm = flower_height_px × cm_per_pixel
```

Current tag size parameter:

```python
'tag_size_cm': 5.0
```

This assumes the printed AprilTag square is about `5 cm × 5 cm`.

For best accuracy, place the AprilTag and flower at roughly the same distance from the camera.

---

## Manual snapshot service call

Instead of pressing `s`, you can call:

```bash
ros2 service call /save_perception_snapshot std_srvs/srv/Trigger {}
```

Expected:

```text
success: true
message: image=/home/nikolaos/ros2_ws/perception_snapshots/....png; json=/home/nikolaos/ros2_ws/perception_snapshots/....json
```

Open saved files:

```bash
xdg-open ~/ros2_ws/perception_snapshots
```

---

## Troubleshooting

### Laptop does not see MIRTE topics

```bash
ros2 daemon stop
ros2 daemon start
ros2 topic list | grep gripper_camera
```

Check both machines:

```bash
echo $ROS_DOMAIN_ID
```

Both should be:

```text
0
```

### `/greenhouse/tag_reading` has no output

Check:

```bash
ros2 node list | grep greenhouse
ros2 service list | grep greenhouse
ros2 topic echo /gripper_camera/tags
```

Expected:

```text
/greenhouse_bridge
/greenhouse_tag_reader
/greenhouse_bridge/get_tag_reading
```

### `/flower_detector/flower_lengths` has `flower_count: 0`

YOLO has not detected a flower. Check:

```bash
ros2 topic echo /flower_detector/detections
```

### `estimated_length_cm` is `null`

No AprilTag scale has been received. Check:

```bash
ros2 topic echo /gripper_camera/tags
```

### Snapshot says no image received

Check:

```bash
ros2 topic hz /perception/image_combined
ros2 node list | grep snapshot
```

---

## Final demo checklist

The system is working when:

```text
/perception/image_combined shows YOLO and AprilTag overlays
/flower_detector/detections publishes flower detections
/gripper_camera/tags publishes AprilTag IDs
/greenhouse/tag_reading publishes greenhouse sensor readings
/flower_detector/flower_lengths publishes estimated_length_px and estimated_length_cm
pressing s saves a PNG image and matching JSON file
```
