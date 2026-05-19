# mdp_mirte_master


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


## Mapping and Saving Greenhouse Map

This section explains how to start the greenhouse simulation, run SLAM mapping, manually control the robot, save the map, and load the saved map again.

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

---

### 2. Launch MIRTE in the greenhouse world

Run this command from the root directory of this repository:

```bash
ros2 launch mirte_gazebo gazebo_mirte_master_empty.launch.xml \
  world:=$(pwd)/worlds/greenhouse.world
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

---

### 3. Start SLAM mapping

Open a new terminal:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch mdp_mapping mapping.launch.py use_sim_time:=true
```

This starts:

```text
slam_toolbox
mapping_manager_node
```

Check whether the map is being published:

```bash
ros2 topic echo --once /map
```

---

### 4. Visualize the map in RViz

Open a new terminal:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

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

---

### 5. Manually control the robot

Open a new terminal:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

If the robot does not move, check the velocity topic:

```bash
ros2 topic list | grep cmd
ros2 topic list | grep vel
```

If needed, remap `/cmd_vel`:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/your_robot_cmd_vel
```

Drive the robot slowly around the greenhouse until the map looks complete in RViz.

---

### 6. Save the map

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
```

---

### 7. Load a saved map

Replace the file name with the actual saved map name:

```bash
ros2 run nav2_map_server map_server --ros-args \
  -p yaml_filename:=/home/zheng/ros2_ws/install/mdp_mapping/share/mdp_mapping/maps/greenhouse_map_YYYYMMDD_HHMMSS.yaml \
  -p use_sim_time:=true
```

Activate the map server:

```bash
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

Check the loaded map:

```bash
ros2 topic echo --once /map
```

View it in RViz:

```bash
rviz2
```

Set:

```text
Fixed Frame: map
```

Add:

```text
/map
```

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











## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/user/project/repository/web_editor/#create-a-file) or [upload](https://docs.gitlab.com/user/project/repository/web_editor/#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.tudelft.nl/cor/ro47007/2026/group_01/mdp_mirte_master.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://gitlab.tudelft.nl/cor/ro47007/2026/group_01/mdp_mirte_master/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/)
* [Automatically close issues from merge requests](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.


