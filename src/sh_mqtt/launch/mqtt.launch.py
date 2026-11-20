"""Kapitel 2: turtlesim, MQTT-Brücke und die beiden Beispielknoten.

    ros2 launch sh_mqtt mqtt.launch.py [broker:=localhost]
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bruecke = os.path.join(get_package_share_directory("sh_mqtt"), "config",
                           "mqtt_bruecke.yaml")
    return LaunchDescription([
        DeclareLaunchArgument("broker", default_value="localhost"),
        Node(package="turtlesim", executable="turtlesim_node", name="turtlesim"),
        Node(package="mqtt_client", executable="mqtt_client", name="mqtt_client",
             output="screen",
             parameters=[bruecke, {"broker.host": LaunchConfiguration("broker")}]),
        Node(package="sh_mqtt", executable="temperatur_farbe", output="screen"),
        Node(package="sh_mqtt", executable="schildkroete_melder", output="screen"),
    ])
