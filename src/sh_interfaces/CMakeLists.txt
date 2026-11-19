cmake_minimum_required(VERSION 3.8)
project(sh_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Raumklima.msg"
  "srv/LichtSzene.srv"
  "action/Kontrollgang.action"
  DEPENDENCIES std_msgs
)
ament_export_dependencies(rosidl_default_runtime)
ament_package()
