"""Kapitel 13 und 16: Bildrate und Datenrate beliebiger Topics messen.

    ros2 run sh_kamera bandbreite --ros-args \
        -p themen:="[/kinect_v1/rgb/image_raw, /kinect_v1/depth/image_raw]" -p sekunden:=5.0
"""
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_sensor_data
from rosidl_runtime_py.utilities import get_message


class Bandbreite(Node):
    def __init__(self):
        super().__init__("bandbreite")
        self.themen = self.declare_parameter("themen", ["/kinect_v1/rgb/image_raw"]).value
        self.sekunden = self.declare_parameter("sekunden", 5.0).value
        # best effort passt zu jedem Publisher, verliert bei großen Bildern aber Nachrichten
        # (Kapitel 16) – reliable misst ohne Verluste, passt aber nur zu reliable-Publishern
        zuverlaessig = self.declare_parameter("reliable", False).value
        self.qos = QoSProfile(depth=5) if zuverlaessig else qos_profile_sensor_data
        self.zaehler = {t: [0, 0] for t in self.themen}   # Nachrichten, Bytes
        self.offen = list(self.themen)
        self.start = time.monotonic()
        self.create_timer(0.5, self.verbinden)
        self.create_timer(self.sekunden, self.ausgeben)

    def verbinden(self):
        """Typ erst abfragen, wenn das Topic existiert – dann passend abonnieren."""
        typen = dict(self.get_topic_names_and_types())
        for thema in list(self.offen):
            if thema in typen:
                typ = get_message(typen[thema][0])
                self.create_subscription(typ, thema, lambda m, t=thema: self.zaehlen(t, m),
                                         self.qos, raw=True)
                self.offen.remove(thema)

    def zaehlen(self, thema, roh):
        z = self.zaehler[thema]
        z[0] += 1
        z[1] += len(roh)                                  # serialisierte Größe in Bytes

    def ausgeben(self):
        dauer = time.monotonic() - self.start
        gesamt = 0.0
        for thema, (n, b) in self.zaehler.items():
            gesamt += b / dauer / 1e6
            self.get_logger().info(f"{thema:<38} {n / dauer:5.1f} Hz {b / dauer / 1e6:7.2f} MB/s")
        self.get_logger().info(f"{'gesamt':<38} {'':8} {gesamt:7.2f} MB/s")
        self.zaehler = {t: [0, 0] for t in self.themen}
        self.start = time.monotonic()


def main(args=None):
    rclpy.init(args=args)
    knoten = Bandbreite()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
