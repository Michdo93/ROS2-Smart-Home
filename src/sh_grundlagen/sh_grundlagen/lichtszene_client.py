"""Kapitel 6: Service-Client – ruft eine Lichtszene auf und wartet auf die Antwort.

    ros2 run sh_grundlagen lichtszene_client wohnzimmer kino
"""
import sys

import rclpy
from rclpy.node import Node
from sh_interfaces.srv import LichtSzene


def main(args=None):
    rclpy.init(args=args)
    knoten = Node("lichtszene_client")
    client = knoten.create_client(LichtSzene, "lichtszene")
    if not client.wait_for_service(timeout_sec=5.0):
        knoten.get_logger().error("Service /lichtszene nicht erreichbar")
        sys.exit(1)
    raum, szene = (sys.argv[1:3] + ["wohnzimmer", "lesen"][len(sys.argv[1:3]):])[:2]
    zukunft = client.call_async(LichtSzene.Request(raum=raum, szene=szene))
    rclpy.spin_until_future_complete(knoten, zukunft, timeout_sec=5.0)
    antwort = zukunft.result()
    print(f"erfolg={antwort.erfolg}: {antwort.meldung}" if antwort else "keine Antwort")
    knoten.destroy_node()
    rclpy.try_shutdown()
