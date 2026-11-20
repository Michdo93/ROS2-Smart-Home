"""Kapitel 16: Rohbild -> JPEG (sensor_msgs/CompressedImage) – spart über 90 % Datenrate.

Entspricht dem compressed-Transport von image_transport, ohne C++-Plugins.

    ros2 run sh_kamera kompressor --ros-args -p bild:=/kinect_v1/rgb/image_raw \
        -p qualitaet:=80
"""
import cv2
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image

from .bildwandler import bild_zu_array


class Kompressor(Node):
    def __init__(self):
        super().__init__("kompressor")
        thema = self.declare_parameter("bild", "/kinect_v1/rgb/image_raw").value
        self.qualitaet = self.declare_parameter("qualitaet", 80).value
        self.pub = self.create_publisher(CompressedImage, thema + "/compressed", 2)
        self.create_subscription(Image, thema, self.bild, 2)

    def bild(self, m):
        if m.encoding not in ("rgb8", "bgr8", "mono8"):
            return
        pixel = bild_zu_array(m)                          # Kapitel 13
        if m.encoding == "rgb8":
            pixel = pixel[..., ::-1]                      # OpenCV erwartet BGR
        ok, jpeg = cv2.imencode(".jpg", pixel, [cv2.IMWRITE_JPEG_QUALITY, self.qualitaet])
        if ok:
            self.pub.publish(CompressedImage(header=m.header, format="jpeg",
                                             data=jpeg.tobytes()))


def main(args=None):
    rclpy.init(args=args)
    knoten = Kompressor()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
