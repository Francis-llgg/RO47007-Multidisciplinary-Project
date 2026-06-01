cmake_minimum_required(VERSION 3.8)
project(mission_planner_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/scan.action"
)
ament_python_install_package(${PROJECT_NAME})


install(PROGRAMS
  mission_planner/mission_planner_node.py
  mission_planner/scan_action_server.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()