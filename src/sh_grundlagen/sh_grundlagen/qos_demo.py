"""Kapitel 6: QoS – wer zu spät abonniert, bekommt den letzten Zustand
nur mit "transient local".

    ros2 run sh_grundlagen qos_demo
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from std_msgs.msg import String

FLUECHTIG = QoSProfile(depth=1, durability=DurabilityPolicy.VOLATILE)
DAUERHAFT = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)


def main(args=None):
    rclpy.init(args=args)
    knoten = Node("qos_demo")
    for name, qos in (("fluechtig", FLUECHTIG), ("dauerhaft", DAUERHAFT)):
        knoten.create_publisher(String, f"tuer/{name}", qos).publish(String(data="OPEN"))
    print("Zustand OPEN gesendet – jetzt erst abonnieren ...")
    empfangen = {}
    for name, qos in (("fluechtig", FLUECHTIG), ("dauerhaft", DAUERHAFT)):
        knoten.create_subscription(String, f"tuer/{name}",
                                   lambda m, n=name: empfangen.setdefault(n, m.data), qos)
    for _ in range(20):                                  # zwei Sekunden warten
        rclpy.spin_once(knoten, timeout_sec=0.1)
    for name in ("fluechtig", "dauerhaft"):
        print(f"  {name:<10} -> {empfangen.get(name, 'nichts empfangen')}")
    knoten.destroy_node()
    rclpy.try_shutdown()
