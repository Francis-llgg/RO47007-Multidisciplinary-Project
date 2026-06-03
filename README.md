# mdp_mirte_master


<details> 
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
</details>

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
</details>
<details>
<summary>Mapping and Saving Greenhouse Map</summary>

### 1. Build and source the workspace

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
````

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
````

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
</details>

<details>
<summary>Localization in Greenhouse Map</summary>

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


