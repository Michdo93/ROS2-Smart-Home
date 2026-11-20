"""Kapitel 15: Tiefenbild auswerten – wie weit ist das Nächste in der Bildmitte entfernt?

    ros2 run sh_kamera abstand --ros-args -p tiefe:=/kinect_v1/depth/image_raw
"""
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32

from .bildwandler import bild_zu_array


class Abstand(Node):
    def __init__(self):
        super().__init__("abstand")
        thema = self.declare_parameter("tiefe", "/kinect_v1/depth/image_raw").value
        self.pub = self.create_publisher(Float32, "abstand", 10)
        self.create_subscription(Image, thema, self.tiefe, 2)
        self.zaehler = 0

    def tiefe(self, m):
        mm = bild_zu_array(m)                         # uint16, Millimeter, 0 = unbekannt
        h, w = mm.shape
        mitte = mm[h // 2 - 20 : h // 2 + 20, w // 2 - 20 : w // 2 + 20]
        gueltig = mitte[mitte > 0]
        if gueltig.size == 0:
            return
        meter = float(np.percentile(gueltig, 10)) / 1000.0   # robust gegen Ausreißer
        self.pub.publish(Float32(data=meter))
        self.zaehler += 1
        if self.zaehler % 30 == 1:                    # etwa einmal pro Sekunde
            self.get_logger().info(
                f"{m.width}x{m.height} {m.encoding}, Mitte: {meter:.2f} m, "
                f"{100 * gueltig.size / mitte.size:.0f} % gültig")


def main(args=None):
    rclpy.init(args=args)
    knoten = Abstand()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    except Exception:
        if rclpy.ok():   # beim Beenden harmlos: der Kontext ist schon geschlossen
            raise
    finally:
        try:
            knoten.destroy_node()
            rclpy.try_shutdown()
        except KeyboardInterrupt:   # zweites Strg+C beim Beenden
            pass
