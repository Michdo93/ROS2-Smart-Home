"""Kapitel 17: Kinect -> hand_detektor -> openHAB-Brücke -> Item Flur_Hand.

    ros2 launch sh_hand hand.launch.py simulate:=true          # ohne Kinect
    ros2 launch sh_hand hand.launch.py kamera:=v2              # Kinect v2
OPENHAB_URL und OPENHAB_TOKEN müssen gesetzt sein.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EqualsSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def treiber(version):
    paket = f"kinect_{version}_ros2"
    datei = os.path.join(get_package_share_directory(paket), "launch",
                         f"kinect_{version}.launch.py")
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(datei),
        launch_arguments={"simulate": LaunchConfiguration("simulate")}.items(),
        condition=IfCondition(EqualsSubstitution(LaunchConfiguration("kamera"), version)))


def generate_launch_description():
    bruecke = os.path.join(get_package_share_directory("sh_hand"), "config",
                           "bruecke_hand.yaml")
    tiefe = PythonExpression(["'/kinect_' + '", LaunchConfiguration("kamera"),
                              "' + '/depth/image_raw'"])
    return LaunchDescription([
        DeclareLaunchArgument("kamera", default_value="v1", description="v1 oder v2"),
        DeclareLaunchArgument("simulate", default_value="false"),
        treiber("v1"),
        treiber("v2"),
        Node(package="sh_hand", executable="hand_detektor", output="screen",
             parameters=[{"tiefe": tiefe}]),
        Node(package="openhab_bridge", executable="openhab_bridge", name="openhab_bridge",
             parameters=[bruecke], output="screen"),
    ])
