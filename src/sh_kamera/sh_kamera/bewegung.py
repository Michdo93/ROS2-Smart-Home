"""Kapitel 18: zweite Anwendung am selben Kamerabild – einfache Bewegungserkennung.

Vergleicht jedes fünfte Bild mit dem vorigen; meldet /bewegung (std_msgs/Bool).

    ros2 run sh_kamera bewegung --ros-args -p bild:=/kinect_v1/rgb/image_raw
"""
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from sensor_msgs.msg import Image
from std_msgs.msg import Bool


class Bewegung(Node):
    def __init__(self):
        super().__init__("bewegung")
        thema = self.declare_parameter("bild", "/kinect_v1/rgb/image_raw").value
        self.schwelle = self.declare_parameter("schwelle", 0.01).value  # Anteil der Pixel
        self.pub = self.create_publisher(
            Bool, "bewegung",
            QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL))
        self.create_subscription(Image, thema, self.bild, 2)
        self.vorher, self.zustand, self.zaehler = None, None, 0

    def bild(self, m):
        self.zaehler += 1
        if self.zaehler % 5:
            return
        grau = np.frombuffer(m.data, np.uint8)[::3].astype(np.int16)  # nur ein Farbkanal
        if self.vorher is not None and len(grau) == len(self.vorher):
            anteil = float(np.mean(np.abs(grau - self.vorher) > 25))
            bewegt = anteil > self.schwelle
            if bewegt != self.zustand:
                self.zustand = bewegt
                self.pub.publish(Bool(data=bewegt))
                self.get_logger().info(f"Bewegung: {bewegt} ({anteil:.1%} der Pixel)")
        self.vorher = grau


def main(args=None):
    rclpy.init(args=args)
    knoten = Bewegung()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
