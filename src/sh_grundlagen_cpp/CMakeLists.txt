cmake_minimum_required(VERSION 3.16)
project(sh_grundlagen_cpp LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sh_interfaces REQUIRED)

# Kapitel 4: CMake-Ziele statt ament_target_dependencies() (gibt es in Lyrical nicht mehr)
foreach(knoten raumklima_sender raumklima_empfaenger)
  add_executable(${knoten} src/${knoten}.cpp)
  target_link_libraries(${knoten} rclcpp::rclcpp ${sh_interfaces_TARGETS})
  install(TARGETS ${knoten} DESTINATION lib/${PROJECT_NAME})
endforeach()

ament_package()
