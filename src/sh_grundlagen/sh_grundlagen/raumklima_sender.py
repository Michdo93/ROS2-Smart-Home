"""Kapitel 5: Publisher – ein simulierter Raumsensor sendet jede Sekunde sein Raumklima.

    ros2 run sh_grundlagen raumklima_sender --ros-args -p raum:=kueche -p intervall:=2.0
"""
import math
import random

import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sh_interfaces.msg import Raumklima


class RaumklimaSender(Node):
    def __init__(self):
        super().__init__("raumklima_sender")
        self.raum = self.declare_parameter("raum", "wohnzimmer").value
        intervall = self.declare_parameter("intervall", 1.0).value
        self.pub = self.create_publisher(Raumklima, "raumklima", 10)
        self.timer = self.create_timer(intervall, self.senden)
        self.add_on_set_parameters_callback(self.parameter_geaendert)  # Kapitel 6
        self.schritt = sum(map(ord, self.raum)) % 60     # jeder Raum startet anders

    def senden(self):
        self.schritt += 1
        m = Raumklima()
        m.header.stamp = self.get_clock().now().to_msg()
        m.raum = self.raum
        m.temperatur = 21.0 + math.sin(self.schritt / 30) + random.uniform(-0.1, 0.1)
        m.luftfeuchte = 45.0 + random.uniform(-2, 2)
        m.co2 = 600 + (self.schritt * 7) % 900          # steigt, bis jemand lüftet
        self.pub.publish(m)
        self.get_logger().info(f"{m.raum}: {m.temperatur:.1f} °C, {m.luftfeuchte:.0f} %, "
                               f"{m.co2} ppm")

    def parameter_geaendert(self, parameter):
        for p in parameter:
            if p.name == "intervall":
                if p.value <= 0:
                    return SetParametersResult(successful=False, reason="intervall > 0")
                self.timer.cancel()
                self.timer = self.create_timer(p.value, self.senden)
            elif p.name == "raum":
                self.raum = p.value
        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    knoten = RaumklimaSender()
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
