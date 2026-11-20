"""Kapitel 5: Subscriber – meldet, wenn in einem Raum gelüftet werden sollte.

    ros2 run sh_grundlagen raumklima_empfaenger --ros-args -p grenze:=1000
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sh_interfaces.msg import Raumklima


class RaumklimaEmpfaenger(Node):
    def __init__(self):
        super().__init__("raumklima_empfaenger")
        self.grenze = self.declare_parameter("grenze", 1000).value
        self.create_subscription(Raumklima, "raumklima", self.empfangen, 10)

    def empfangen(self, m):
        if m.co2 > self.grenze:
            self.get_logger().warn(f"{m.raum}: {m.co2} ppm CO₂ – bitte lüften")


def main(args=None):
    rclpy.init(args=args)
    knoten = RaumklimaEmpfaenger()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
