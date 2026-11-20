"""Kapitel 16: Tag und Nacht – das Licht in openHAB schaltet die Kinect v1 auf RGB oder IR.

Ist das Licht aus, ist es dunkel: Die Kinect liefert dann das Infrarotbild, das ihr eigener
Laser beleuchtet. Geht das Licht an, schaltet sie zurück auf das Farbbild.

    ros2 run sh_kamera tag_nacht --ros-args -p licht:=Wohnzimmer_Licht
"""
import rclpy
from openhab_msgs.msg import ItemState
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.parameter_client import AsyncParameterClient
from rclpy.qos import DurabilityPolicy, QoSProfile

ZUSTAND = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)


class TagNacht(Node):
    def __init__(self):
        super().__init__("tag_nacht")
        licht = self.declare_parameter("licht", "Wohnzimmer_Licht").value
        treiber = self.declare_parameter("treiber", "/kinect_v1/driver").value
        self.kinect = AsyncParameterClient(self, treiber)
        self.modus = None
        self.create_subscription(ItemState, f"/openhab/items/{licht}/state",
                                 self.licht, ZUSTAND)

    def licht(self, m):
        if m.is_null:
            return
        modus = "rgb" if m.has_number and m.number > 0 else "ir"   # Dimmer > 0: an
        if modus == self.modus:
            return
        if not self.kinect.wait_for_services(timeout_sec=2.0):
            self.get_logger().warn("Kinect-Treiber nicht erreichbar")
            return
        self.modus = modus
        zukunft = self.kinect.set_parameters([Parameter("video_mode", value=modus)])
        zukunft.add_done_callback(
            lambda z: self.get_logger().info(
                f"Licht {m.state} -> video_mode {modus}: "
                f"{'ok' if z.result().results[0].successful else 'abgelehnt'}"))


def main(args=None):
    rclpy.init(args=args)
    knoten = TagNacht()
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
