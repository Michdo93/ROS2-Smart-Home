"""Kapitel 16: eine Kamera, viele Anwendungen – alle am selben Kinect-Treiber.

    ros2 launch sh_kamera viele_anwendungen.launch.py simulate:=true
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    kinect = os.path.join(get_package_share_directory("kinect_v1_ros2"), "launch",
                          "kinect_v1.launch.py")
    rgb, tiefe = "/kinect_v1/rgb/image_raw", "/kinect_v1/depth/image_raw"
    return LaunchDescription([
        DeclareLaunchArgument("simulate", default_value="false"),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(kinect), launch_arguments={
            "simulate": LaunchConfiguration("simulate")}.items()),
        Node(package="sh_hand", executable="hand_detektor", parameters=[{"tiefe": tiefe}],
             output="screen"),                                   # Anwendung 1
        Node(package="sh_kamera", executable="bewegung", parameters=[{"bild": rgb}],
             output="screen"),                                   # Anwendung 2
        Node(package="sh_kamera", executable="kompressor", parameters=[{"bild": rgb}]),
        Node(package="sh_kamera", executable="bandbreite", output="screen", parameters=[{
            "themen": [rgb, tiefe, rgb + "/compressed"], "sekunden": 5.0}]),
    ])
