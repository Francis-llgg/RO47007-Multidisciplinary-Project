# Flower and AprilTag Combined Perception Pipeline

This ROS 2 package provides a combined perception pipeline for the MDP MIRTE robot. It runs a YOLO-based flower/bug detector, an AprilTag detector, and a combined visualization node that overlays both detections on one image.

The final combined output is published on:

```text
/perception/image_combined
```

## Package contents

```text
flower_detector/
├── flower_detector/
│   ├── yolo_flower_detector.py
│   └── combined_visualizer.py
├── launch/
│   ├── laptop_combined_perception.launch.py
│   └── mirte_combined_perception.launch.py
├── models/
│   └── best.pt
├── package.xml
└── setup.py
```

## Pipeline overview

### Laptop camera setup

```text
/camera/image_raw
    ├── AprilTag detector → /camera/tags
    ├── YOLO flower detector → /flower_detector/detections
    ↓
/perception/image_combined
```

### MIRTE camera setup

```text
/gripper_camera/image_raw
    ├── AprilTag detector → /gripper_camera/tags
    ├── YOLO flower detector → /flower_detector/detections
    ↓
/perception/image_combined
```

## Dependencies

Install the required ROS 2 packages:

```bash
sudo apt update

sudo apt install python3-pip \
                 ros-humble-cv-bridge \
                 ros-humble-vision-msgs \
                 ros-humble-rqt-image-view \
                 ros-humble-v4l2-camera \
                 ros-humble-apriltag-detector \
                 ros-humble-apriltag-draw \
                 ros-humble-apriltag-detector-umich \
                 ros-humble-apriltag-detector-mit
```

Install the Python dependencies:

```bash
pip install ultralytics opencv-python
```

If `cv_bridge` gives a NumPy-related error, downgrade NumPy:

```bash
pip install --user --force-reinstall "numpy==1.26.4"
```

## Build

From the ROS 2 workspace root:

```bash
cd ~/ros2_ws

source /opt/ros/humble/setup.bash

colcon build --symlink-install --packages-select flower_detector

source ~/ros2_ws/install/setup.bash
```

Check that the launch files are available:

```bash
ros2 launch flower_detector laptop_combined_perception.launch.py --show-args
ros2 launch flower_detector mirte_combined_perception.launch.py --show-args
```

Check that the YOLO model is installed:

```bash
ls ~/ros2_ws/install/flower_detector/share/flower_detector/models/best.pt
```

## Running with the laptop camera

Use this launch file for testing without MIRTE. It starts the laptop webcam, AprilTag detector, YOLO flower detector, and combined visualizer.

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

ros2 launch flower_detector laptop_combined_perception.launch.py
```

View the combined output:

```bash
source /opt/ros/humble/setup.bash

ros2 run rqt_image_view rqt_image_view
```

Select:

```text
/perception/image_combined
```

Optional confidence override:

```bash
ros2 launch flower_detector laptop_combined_perception.launch.py confidence:=0.60
```

## Running with MIRTE

First, make sure the MIRTE gripper camera is running and publishing:

```text
/gripper_camera/image_raw
```

On MIRTE, source ROS and use the same ROS domain as the laptop:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

# Start the gripper camera node/launch here.
```

Check on MIRTE that the camera topic exists:

```bash
ros2 topic list | grep image
ros2 topic hz /gripper_camera/image_raw
```

On the laptop, check that the MIRTE camera topic is visible:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 daemon stop
ros2 daemon start

ros2 topic list | grep image
ros2 topic hz /gripper_camera/image_raw
```

Then launch the full MIRTE perception pipeline on the laptop:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=0

ros2 launch flower_detector mirte_combined_perception.launch.py
```

View the combined output:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

ros2 run rqt_image_view rqt_image_view
```

Select:

```text
/perception/image_combined
```

## Useful checks

List relevant topics:

```bash
ros2 topic list | grep -E "camera|gripper|flower|tag|perception"
```

Check AprilTag detections on the laptop camera:

```bash
ros2 topic echo /camera/tags
```

Check AprilTag detections on the MIRTE camera:

```bash
ros2 topic echo /gripper_camera/tags
```

Check YOLO flower detections:

```bash
ros2 topic echo /flower_detector/detections
```

Check the combined output topic:

```bash
ros2 topic hz /perception/image_combined
```

## Output colors

The combined visualizer uses the following colors:

```text
tulip_red    → blue
tulip_white  → cyan
tulip_pink   → light gray
bug          → cyan
AprilTags    → red
```

## Notes

The AprilTag detector is not implemented inside this package. It is used as an external ROS 2 dependency through:

```bash
ros-humble-apriltag-detector
```

The YOLO weights are included in:

```text
flower_detector/models/best.pt
```

Both launch files use this package-relative model path, so the launch files do not depend on a user-specific local path.
