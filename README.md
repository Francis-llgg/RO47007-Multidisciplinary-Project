# mdp_mirte_master

This repository contains the ROS 2 software, simulation setup, mapping/localization tools, dashboard, and perception pipeline for the Group 01 MDP MIRTE Master greenhouse project. The system is developed for ROS 2 Humble and supports both simulation-based testing and robot-side operation with MIRTE.

## Repository overview

- `dashboard/`: React dashboard for robot monitoring and control.
- `flower_detector/`: YOLO flower/bug detection, AprilTag integration, and combined perception visualizations.
- `greenhouse_setup/`: greenhouse layout and tag configuration files.
- `led_strip/`: battery monitor to change led color if battery is low.
- `maps/`: saved generated greenhouse maps.
- `mdp_interfaces/`:
- `mdp_localization/`: localization configuration.
- `mdp_mapping/`: mapping workflow and map saving tools.
- `mdp_navigation/`: navigation workflow.
- `mirte_launch/`: 
- `mission_planner/`: allows for multiple assignments to the robot.
- `perception_dashboard_bridge/`: connection from flower_detector to the dashboard.

<!-- <details> 
<summary>Set up Virtual Greenhouse Environment</summary>

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
</details> -->

<details>
<summary>Set up MIRTE Dashboard</summary>

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

Build and source the packages:
```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
source /opt/ros/humble/setup.bash
```

If running the dashboard with the Gazebo simulation:
1. Start the Gazebo simulation
2. Launch the dashboard using the launch file:
```bash
ros2 launch dashboard simulation.launch.py
```

If running the dashboard with the robot:
1. Launch the dashboard using the launch file:
```bash
ros2 launch dashboard robot.launch.py
```
2. If using an ethernet cable to connect to the robot:
```bash
ros2 launch dashboard robot.launch.py network:='ethernet'
```

### Opening the Dashboard

1. On your laptop/desktop browser open:
```text
http://localhost:5173
```

---
</details>




<details>
<summary>Mapping and Localization in Greenhouse Map</summary>

### Setup environment
```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
```

### Mapping (start everything: Gazebo, 
```bashslam_toolbox, scan filter, Nav2, RViz)
ros2 launch mdp_mapping mapping.launch.py world:=/home/zheng/ros2_ws/src/mdp_mirte_master/greenhouse_simulation/worlds/greenhouse.world
```

### Automatic mapping (run in mdp_mirte_master directory)
```bash
ros2 run explore_lite explore \
  --ros-args \
  -p use_sim_time:=true \
  --params-file ~/ros2_ws/src/m-explore-ros2/explore/config/params.yaml
  ```

### Save map (after /map is being published)
```bash
ros2 service call /save_map std_srvs/srv/Trigger {}
```

### Localization — AMCL
```bash
ros2 launch mdp_localization localization_amcl.launch.py
```

### Localization — slam_toolbox
```bash
ros2 launch mdp_localization localization_slamtoolbox.launch.py
```

</details>

<details>
<Summary>Launching Mirte with navigation, Rviz (and simulation)</summary>
To use this, you first have to build and install the mirte_launch package in your ros2 workspace.

To launch the MIRTE robot with navigation in the simulation and Rviz, use the following command:

```bash
ros2 launch mirte_launch mirte_sim.launch.py
```
This command will start the MIRTE robot in the Gazebo simulation environment, along with the nav2 stack with correct paramters found in mirte_launch/config/nav2_params and visualization in Rviz.

The parameters for the navigation stack are configured in `mirte_launch/config/nav2_params`. You can modify these parameters to adjust the behavior of the navigation stack as needed.

If launching the mirte in real life, use: 
```bash
ros2 launch mirte_launch mirte.launch.py
```
</details>

<details>
<summary>Launching the MissionPlanner</summary>
This package will make the robot go through every pose in the file: 'mission_planner/config/tables.yaml'. When at a pose it will capture the latest recieved image and save it to '~/scan_images'.

Launching the package can be done through:
```bash
ros2 launch mission_planner mission_planner.launch.py
```
</details>


This repository is under active development during the RO47007 Multidisciplinary Project.
