"""Kapitel 19: hand_detektor – Tiefenbild rein, /hand_erkannt raus.

    ros2 run sh_hand hand_detektor --ros-args -p tiefe:=/kinect_v1/depth/image_raw
"""
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from sensor_msgs.msg import Image
from std_msgs.msg import Bool

from .erkennung import Entpreller, hand_im_bild

ZUSTAND = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)


class HandDetektor(Node):
    def __init__(self):
        super().__init__("hand_detektor")
        thema = self.declare_parameter("tiefe", "/kinect_v1/depth/image_raw").value
        self.jedes = self.declare_parameter("jedes_bild", 3).value   # 30 Hz -> 10 Hz
        self.entprellen = Entpreller(self.declare_parameter("entprellen", 3).value)
        self.pub = self.create_publisher(Bool, "hand_erkannt", ZUSTAND)
        self.pub_pos = self.create_publisher(PointStamped, "hand_position", 10)
        self.create_subscription(Image, thema, self.bild, 2)
        self.zaehler = 0
        self.pub.publish(Bool(data=False))
        self.get_logger().info(f"warte auf {thema}")

    def bild(self, m):
        self.zaehler += 1
        if m.encoding != "16UC1" or self.zaehler % self.jedes:
            return
        zeilen = np.frombuffer(m.data, np.uint16).reshape(m.height, m.step // 2)
        tiefe = zeilen[:, : m.width]                        # Füllbytes abschneiden
        erkannt, x, y = hand_im_bild(tiefe)
        if erkannt:
            p = PointStamped(header=m.header)
            p.point.x, p.point.y = x, y
            self.pub_pos.publish(p)
        wechsel = self.entprellen(erkannt)
        if wechsel is not None:
            self.pub.publish(Bool(data=wechsel))
            self.get_logger().info("Hand erkannt" if wechsel else "Hand weg")


def main(args=None):
    rclpy.init(args=args)
    knoten = HandDetektor()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        try:
            knoten.destroy_node()
            rclpy.try_shutdown()
        except KeyboardInterrupt:   # zweites Strg+C beim Beenden
            pass
