"""Kapitel 14: turtlesim als Roboter, openHAB-Brücke und der Haus-Roboter.

    ros2 launch sh_szenarien roboter.launch.py
OPENHAB_URL und OPENHAB_TOKEN müssen gesetzt sein.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    bruecke = os.path.join(get_package_share_directory("sh_szenarien"), "config",
                           "bruecke_roboter.yaml")
    return LaunchDescription([
        Node(package="turtlesim", executable="turtlesim_node", name="turtlesim"),
        Node(package="openhab_bridge", executable="openhab_bridge",
             name="openhab_bridge", parameters=[bruecke], output="screen"),
        Node(package="sh_szenarien", executable="haus_roboter", output="screen"),
    ])
