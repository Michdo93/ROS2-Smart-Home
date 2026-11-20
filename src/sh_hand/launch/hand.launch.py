"""Kapitel 19: Kinect -> hand_detektor -> openHAB oder Home Assistant.

    ros2 launch sh_hand hand.launch.py simulate:=true          # ohne Kinect
    ros2 launch sh_hand hand.launch.py kamera:=v2              # Kinect v2
    ros2 launch sh_hand hand.launch.py ziel:=mqtt              # Home Assistant
Für openHAB müssen OPENHAB_URL und OPENHAB_TOKEN gesetzt sein.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, GroupAction,
                            IncludeLaunchDescription, SetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (EqualsSubstitution, LaunchConfiguration,
                                  PythonExpression)
from launch_ros.actions import Node


def treiber(version):
    paket = f"kinect_{version}_ros2"
    datei = os.path.join(get_package_share_directory(paket), "launch",
                         f"kinect_{version}.launch.py")
    # Mit SROS2 (Kapitel 21) bekommt der Treiber seine Enclave, sonst wirkungslos
    return GroupAction([
        SetEnvironmentVariable("ROS_SECURITY_ENCLAVE_OVERRIDE",
                               f"/kinect_{version}/driver"),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(datei),
            launch_arguments={"simulate": LaunchConfiguration("simulate")}.items())],
        condition=IfCondition(
            EqualsSubstitution(LaunchConfiguration("kamera"), version)))


def generate_launch_description():
    config = os.path.join(get_package_share_directory("sh_hand"), "config")
    ziel = LaunchConfiguration("ziel")
    tiefe = PythonExpression(["'/kinect_' + '", LaunchConfiguration("kamera"),
                              "' + '/depth/image_raw'"])
    return LaunchDescription([
        DeclareLaunchArgument("kamera", default_value="v1", description="v1 oder v2"),
        DeclareLaunchArgument("simulate", default_value="false"),
        DeclareLaunchArgument("ziel", default_value="openhab",
                              description="openhab oder mqtt"),
        treiber("v1"),
        treiber("v2"),
        Node(package="sh_hand", executable="hand_detektor", output="screen",
             parameters=[{"tiefe": tiefe}],
             ros_arguments=["--enclave", "/hand_detektor"]),
        Node(package="openhab_bridge", executable="openhab_bridge",
             name="openhab_bridge",
             parameters=[os.path.join(config, "bruecke_hand.yaml")], output="screen",
             ros_arguments=["--enclave", "/openhab_bridge"],
             condition=IfCondition(EqualsSubstitution(ziel, "openhab"))),
        Node(package="mqtt_client", executable="mqtt_client", name="mqtt_client",
             parameters=[os.path.join(config, "mqtt_hand.yaml")], output="screen",
             ros_arguments=["--enclave", "/mqtt_client"],
             condition=IfCondition(EqualsSubstitution(ziel, "mqtt"))),
    ])
