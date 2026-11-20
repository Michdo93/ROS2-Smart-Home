"""Kapitel 13: Brücke starten und alle Item-Zustände mit rosbag2 aufzeichnen.

    ros2 launch sh_szenarien aufzeichnung.launch.py ziel:=~/aufnahmen/haus
    ros2 bag info ~/aufnahmen/haus
    ros2 bag play ~/aufnahmen/haus      # Zustände später erneut abspielen
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bruecke = os.path.join(get_package_share_directory("sh_szenarien"), "config",
                           "bruecke_szenarien.yaml")
    return LaunchDescription([
        DeclareLaunchArgument("ziel", default_value="haus_aufnahme"),
        Node(package="openhab_bridge", executable="openhab_bridge",
             name="openhab_bridge", parameters=[bruecke], output="screen"),
        # rosbag2 als Knoten: wie "ros2 bag record --regex ... --output ziel"
        Node(package="rosbag2_transport", executable="recorder", name="aufzeichnung",
             parameters=[{"record.regex": "/openhab/items/.*/state",
                          "storage.uri": LaunchConfiguration("ziel")}],
             output="screen"),
    ])
