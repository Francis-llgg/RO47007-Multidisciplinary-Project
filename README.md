# mdp_mirte_master

This repository contains the ROS 2 software, simulation setup, mapping/localization tools, dashboard, and perception pipeline for the Group 01 MDP MIRTE Master greenhouse project. The system is developed for ROS 2 Humble and supports both simulation-based testing and robot-side operation with MIRTE.

## Repository overview

- `greenhouse_setup/`: greenhouse layout and tag configuration files.
- `worlds/`: generated Gazebo greenhouse worlds.
- `scripts/`: helper scripts, including world generation.
- `mirte_dashboard/`: React dashboard for robot monitoring and control.
- `mdp_mapping/`: mapping workflow and map saving tools.
- `mdp_localization/`: localization configuration.
- `flower_detector/`: YOLO flower/bug detection, AprilTag integration, and combined perception visualization.

## Set up Virtual Greenhouse Environment

This project uses `mdp-greenhouse` to define the virtual greenhouse layout. The layout is stored in `greenhouse_setup/`, then converted into a Gazebo world file using a Python script.

### 1. Install dependencies

From the root directory of this repository, run:

```bash
python3 -m pip install --user -r requirements.txt
```

If the `mdp-greenhouse` command is not found, add the local Python binary folder to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Edit the greenhouse layout

Open the greenhouse editor:

```bash
mdp-greenhouse --edit greenhouse_setup
```

In this editor, tables and sensor tags can be added or modified. After saving, the files in `greenhouse_setup/` will be updated:

```text
greenhouse_config.yaml
tag_locations.json
```

To quickly check the layout:

```bash
mdp-greenhouse --view greenhouse_setup
```

### 3. Generate the Gazebo world

After editing the greenhouse layout, generate the Gazebo world file:

```bash
python3 scripts/generate_greenhouse_world.py
```

This creates or updates:

```text
worlds/greenhouse.world
```

### 4. Launch MIRTE in the greenhouse world

Start the MIRTE Gazebo simulation with the generated greenhouse world:

```bash
ros2 launch mirte_gazebo gazebo_mirte_master_empty.launch.xml \
  world:=$(pwd)/worlds/greenhouse.world
```

Make sure this command is executed from the root directory of this repository.

### 5. Read virtual sensor tag data

List all available tags:

```bash
mdp-greenhouse --read --list-tags --config-folder greenhouse_setup
```

Read data from a specific tag:

```bash
mdp-greenhouse --read <tag_id> --config-folder greenhouse_setup
```

Replace `<tag_id>` with the actual tag ID shown in the tag list.

### Workflow summary

```text
Edit layout in mdp-greenhouse
        ↓
Save greenhouse_setup files
        ↓
Generate worlds/greenhouse.world
        ↓
Launch MIRTE with the generated Gazebo world
```

## Set up MIRTE Dashboard

A React-based dashboard for monitoring and controlling the MIRTE robot in a ROS2 + Gazebo simulation.

### Install dashboard dependencies

This project requires **Node.js 22**. Check your version:

```bash
node -v
npm -v
```

Expected output:
```bash
v22.x.x
10.x.x
```

If versions correct: continue to step 1

If **npm** not installed:

```bash
sudo apt install npm
```

If **node** not installed:

```bash
sudo apt install nodejs
```

Verify version:
```bash
node -v
npm -v
```

If versions incorrect: install **nvm** version 22:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
nvm alias default 22
```

1. Go to dashboard folder:

```bash
cd mirte_dashboard
```

2. Install required packages:
```bash
npm install
```

### Running the Dashboard

1. Start the MIRTE simulation in Gazebo
2. In a seperate terminal: Start rosbridge
```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```
3. In a seperate terminal: Start the React dashboard
```bash
cd mirte_dashboard
npm run dev -- --host
```

### Opening the Dashboard

1. On your laptop/desktop browser open:
```text
http://localhost:5173
```

---

## Flower and AprilTag Combined Perception Pipeline

The `flower_detector` package runs the greenhouse perception pipeline. It combines:

- YOLO-based detection for flowers and bugs,
- AprilTag detection for greenhouse/station references,
- a combined visualizer that overlays all detections on a single image topic.

The final visualization is published on:

```text
/perception/image_combined
```

### Package contents

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

### Perception topic structure

For laptop-camera testing:

```text
/camera/image_raw
    ├── AprilTag detector       → /camera/tags
    ├── YOLO flower detector    → /flower_detector/detections
    └── Combined visualizer     → /perception/image_combined
```

For MIRTE operation:

```text
/gripper_camera/image_raw
    ├── AprilTag detector       → /gripper_camera/tags
    ├── YOLO flower detector    → /flower_detector/detections
    └── Combined visualizer     → /perception/image_combined
```

### Install perception dependencies

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

If `cv_bridge` crashes with a NumPy-related error, use:

```bash
pip install --user --force-reinstall "numpy==1.26.4"
```

### Build the perception package

From the workspace root:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select flower_detector
source install/setup.bash
```

Check that the launch files are available:

```bash
ros2 launch flower_detector laptop_combined_perception.launch.py --show-args
ros2 launch flower_detector mirte_combined_perception.launch.py --show-args
```

Check that the YOLO model is installed with the package:

```bash
ls ~/ros2_ws/install/flower_detector/share/flower_detector/models/best.pt
```

### Run perception with the laptop camera

Use this mode for testing without MIRTE:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch flower_detector laptop_combined_perception.launch.py
```

To view the combined output:

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

### Run perception with MIRTE

First start the MIRTE gripper camera. The perception pipeline expects this topic:

```text
/gripper_camera/image_raw
```

On MIRTE:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0

# Start the MIRTE gripper camera node/launch here.
```

Check on MIRTE:

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

To view the combined output:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=0
ros2 run rqt_image_view rqt_image_view
```

Select:

```text
/perception/image_combined
```

### Useful perception checks

List relevant perception topics:

```bash
ros2 topic list | grep -E "camera|gripper|flower|tag|perception"
```

Check AprilTag detections with the laptop camera:

```bash
ros2 topic echo /camera/tags
```

Check AprilTag detections with the MIRTE gripper camera:

```bash
ros2 topic echo /gripper_camera/tags
```

Check YOLO detections:

```bash
ros2 topic echo /flower_detector/detections
```

Check combined image rate:

```bash
ros2 topic hz /perception/image_combined
```

### Detection colors

The combined visualizer uses the following overlay colors:

```text
tulip_red    → blue
tulip_white  → cyan
tulip_pink   → light gray
bug          → cyan
AprilTags    → red
```

### Notes

The AprilTag detector itself is not implemented in this repository. It is used as an external ROS 2 dependency through `ros-humble-apriltag-detector`.

The YOLO weights are included in:

```text
flower_detector/models/best.pt
```

Both launch files use a package-relative model path, so the pipeline does not depend on a user-specific local training path.

---

## Mapping and Saving Greenhouse Map

### 1. Build and source the workspace

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Every new terminal should run:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```


### 2. Launch MIRTE in the greenhouse world

Run this command from the root directory of this repository:

```bash
ros2 launch mirte_gazebo gazebo_mirte_master_empty.launch.xml world:=$(pwd)/worlds/greenhouse.world
```

Check required topics:

```bash
ros2 topic list
```

The following topics should exist:

```text
/scan
/odom
/tf
/tf_static
```


### 3. Start SLAM mapping

Open a new terminal:

```bash
ros2 launch mdp_mapping mapping.launch.py use_sim_time:=true
```

<!-- This starts:

```text
slam_toolbox
mapping_manager_node
```

Check whether the map is being published:

```bash
ros2 topic echo --once /map
``` -->


### 4. Visualize the map in RViz

Open a new terminal:

```bash
rviz2
```

In RViz:

```text
Fixed Frame: map
```

Add:

```text
/map
/scan
TF
```

### 5. Manually control the robot

Open a new terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel_unstamped
```
Drive the robot slowly around the greenhouse until the map looks complete in RViz.

<!-- ### 6. Save the map

When the map is complete, run:

```bash
ros2 service call /save_map std_srvs/srv/Trigger {}
```

The saved map will contain two files:

```text
greenhouse_map_YYYYMMDD_HHMMSS.yaml
greenhouse_map_YYYYMMDD_HHMMSS.pgm
```

Check saved maps:

```bash
ls ~/ros2_ws/install/mdp_mapping/share/mdp_mapping/maps
``` -->


### 6. Save the Map

After finishing the mapping process, open a new terminal and run:

```bash
ros2 service call /save_map std_srvs/srv/Trigger {}
```

This command saves all map outputs generated by the mapping workflow, including the serialized pose graph, the raw occupancy map, and the filtered occupancy map.

The files are saved by default in:

```text
~/ros2_ws/maps/mdp_mapping/
```

The expected output structure is:

```text
~/ros2_ws/maps/mdp_mapping/
├── posegraph/
│   ├── greenhouse_map_YYYYMMDD_HHMMSS.posegraph
│   └── greenhouse_map_YYYYMMDD_HHMMSS.data
├── raw/
│   ├── greenhouse_map_YYYYMMDD_HHMMSS_raw.pgm
│   └── greenhouse_map_YYYYMMDD_HHMMSS_raw.yaml
└── filtered/
    ├── greenhouse_map_YYYYMMDD_HHMMSS_filtered.pgm
    └── greenhouse_map_YYYYMMDD_HHMMSS_filtered.yaml
```

#### Output files

The `posegraph/` folder contains the serialized pose graph generated by `slam_toolbox`.

These files are required when using `slam_toolbox` in localization mode. When passing the map file to `slam_toolbox`, use the base path without the `.posegraph` suffix:

```bash
~/ros2_ws/maps/mdp_mapping/posegraph/greenhouse_map_YYYYMMDD_HHMMSS
```

The `raw/` folder contains the original occupancy grid map saved directly from the `/map` topic.

This map is useful for debugging and comparison before post-processing.

The `filtered/` folder contains the post-processed occupancy grid map.

The filtered map removes small isolated obstacle points and produces cleaner obstacle boundaries. It can be used for visualization, documentation, or localization methods based on `map_server` and `AMCL`.

#### Notes

The serialized pose graph is used for `slam_toolbox` localization.

The filtered `.pgm` and `.yaml` map files do not modify the pose graph. They are only post-processed occupancy maps.

If the filtered map is used for navigation or AMCL localization, use the `.yaml` file in the `filtered/` folder:

```bash
~/ros2_ws/maps/mdp_mapping/filtered/greenhouse_map_YYYYMMDD_HHMMSS_filtered.yaml
```

---

## Localization in Greenhouse Map

### 1. Build and source the workspace

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Every new terminal should run:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

### 2. Launch MIRTE in the greenhouse world

Run this command from the root directory of this repository:

```bash
ros2 launch mirte_gazebo gazebo_mirte_master_empty.launch.xml world:=$(pwd)/greenhouse_simulation/worlds/greenhouse.world
```


### 3. Start localization: slam_toolbox localization
slam_toolbox localization uses the serialized pose graph:

```text
.posegraph
```

Start slam_toolbox localization:

```bash
ros2 launch slam_toolbox localization_launch.py \
  slam_params_file:=$(pwd)/mdp_localization/config/slam_toolbox_localization.yaml \
  use_sim_time:=true
```
slam_toolbox localization publishes the `map -> odom` transform.

### 4. Visualize localization in RViz

Open a new terminal:

```bash
rviz2
```

In RViz:

```text
Fixed Frame: map
```

Add:

```text
Map        -> /map
LaserScan  -> /scan
RobotModel
TF
```
Use `2D Pose Estimate` in RViz to set the initial robot pose.


### 5. Manually control the robot

Open a new terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/mirte_base_controller/cmd_vel_unstamped
```
Drive the robot slowly around the greenhouse and check whether the laser scan aligns with the map in RViz.


---
---

### Workflow summary

```text
Launch greenhouse simulation
        ↓
Start mapping.launch.py
        ↓
Control robot manually
        ↓
Check /map in RViz
        ↓
Call /save_map
        ↓
Load saved map with nav2_map_server
```

---

## General development workflow

After pulling new code or changing packages, rebuild and source the workspace:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Every new terminal should source ROS 2 and the workspace before running package commands:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

## Contributing

Development should be done on feature branches. Create a branch from `main`, commit changes there, push the branch to GitLab, and open a merge request when the feature is ready for review.

Example:

```bash
git checkout main
git pull origin main
git checkout -b feature/<feature_name>
# make changes
git add <changed_files>
git commit -m "Describe the change"
git push -u origin feature/<feature_name>
```

## Support

For project-specific questions, contact the Group 01 team members or use the project communication channel agreed by the team. For general ROS issues, include the command used, the full terminal output, and the relevant topic/node names when asking for help.

## Project status

This repository is under active development during the RO47007 Multidisciplinary Project.
