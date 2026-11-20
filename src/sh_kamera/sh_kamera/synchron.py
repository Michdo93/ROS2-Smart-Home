"""Kapitel 15: Farb- und Tiefenbild zeitlich zusammenführen (message_filters).

Farbe und Tiefe kommen von zwei Topics mit eigenen Zeitstempeln. Der
ApproximateTimeSynchronizer liefert Paare, deren Zeitstempel höchstens 'toleranz'
auseinander liegen – nur dann gehört ein Pixel im Tiefenbild zum selben Moment wie das Farbbild.

    ros2 run sh_kamera synchron
"""
import message_filters
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image

from .bildwandler import bild_zu_array


def sekunden(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


class Synchron(Node):
    def __init__(self):
        super().__init__("synchron")
        ns = self.declare_parameter("kamera", "/kinect_v1").value
        toleranz = self.declare_parameter("toleranz", 0.02).value     # Sekunden
        farbe = message_filters.Subscriber(self, Image, f"{ns}/rgb/image_raw")
        tiefe = message_filters.Subscriber(self, Image, f"{ns}/depth/image_raw")
        self.sync = message_filters.ApproximateTimeSynchronizer(
            [farbe, tiefe], queue_size=10, slop=toleranz)
        self.sync.registerCallback(self.paar)
        self.paare = 0

    def paar(self, farbe, tiefe):
        self.paare += 1
        if self.paare % 30 != 1:
            return
        rgb, mm = bild_zu_array(farbe), bild_zu_array(tiefe)
        y, x = mm.shape[0] // 2, mm.shape[1] // 2      # registriert: gleiche Pixel
        versatz = abs(sekunden(farbe.header.stamp) - sekunden(tiefe.header.stamp)) * 1000
        self.get_logger().info(
            f"Paar {self.paare}: Versatz {versatz:.1f} ms, "
            f"Mitte RGB {rgb[y, x].tolist()}, {mm[y, x]} mm")


def main(args=None):
    rclpy.init(args=args)
    knoten = Synchron()
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
