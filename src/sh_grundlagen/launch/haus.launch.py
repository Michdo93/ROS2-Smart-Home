"""Kapitel 7: drei Räume, ein Empfänger – Namespaces und Remapping.

    ros2 launch sh_grundlagen haus.launch.py grenze:=900
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    raeume = ["wohnzimmer", "kueche", "bad"]
    sender = [Node(package="sh_grundlagen", executable="raumklima_sender", namespace=raum,
                   parameters=[{"raum": raum, "intervall": 2.0}],
                   remappings=[("raumklima", "/haus/raumklima")]) for raum in raeume]
    empfaenger = Node(package="sh_grundlagen", executable="raumklima_empfaenger",
                      parameters=[{"grenze": LaunchConfiguration("grenze")}],
                      remappings=[("raumklima", "/haus/raumklima")], output="screen")
    return LaunchDescription([DeclareLaunchArgument("grenze", default_value="1000"),
                              *sender, empfaenger])
