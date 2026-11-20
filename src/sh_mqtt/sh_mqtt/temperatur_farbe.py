"""Kapitel 2: Ein Zustand aus dem Smart Home verändert etwas in ROS 2.

Die Solltemperatur aus Home Assistant oder openHAB kommt über MQTT als
std_msgs/Float64.
Der Knoten färbt damit den Hintergrund von turtlesim: 16 °C blau, 26 °C rot.
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.parameter_client import AsyncParameterClient
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Float64
from std_srvs.srv import Empty

ZUSTAND = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                     durability=DurabilityPolicy.TRANSIENT_LOCAL)


def farbe(grad):
    """16 °C -> (40, 80, 255) blau, 26 °C -> (255, 80, 40) rot, dazwischen linear."""
    t = min(1.0, max(0.0, (grad - 16.0) / 10.0))
    return int(40 + 215 * t), 80, int(255 - 215 * t)


class TemperaturFarbe(Node):
    def __init__(self):
        super().__init__("temperatur_farbe")
        self.turtlesim = AsyncParameterClient(self, "/turtlesim")
        self.loeschen = self.create_client(Empty, "/clear")
        self.create_subscription(Float64, "/haus/solltemperatur", self.solltemperatur,
                                 ZUSTAND)

    def solltemperatur(self, msg):
        r, g, b = farbe(msg.data)
        self.get_logger().info(
            f"Solltemperatur {msg.data:.1f} °C -> Hintergrund ({r}, {g}, {b})")
        self.turtlesim.wait_for_services(timeout_sec=5.0)
        zukunft = self.turtlesim.set_parameters([
            Parameter("background_r", value=r),
            Parameter("background_g", value=g),
            Parameter("background_b", value=b)])
        # neu zeichnen, sobald die Farbe gesetzt ist
        zukunft.add_done_callback(lambda _: self.loeschen.call_async(Empty.Request()))


def main(args=None):
    rclpy.init(args=args)
    knoten = TemperaturFarbe()
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
