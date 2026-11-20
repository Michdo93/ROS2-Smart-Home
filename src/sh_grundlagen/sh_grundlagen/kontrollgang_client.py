"""Kapitel 6: Action-Client – startet einen Kontrollgang und zeigt die Rückmeldungen.

    ros2 run sh_grundlagen kontrollgang_client flur kueche wohnzimmer
"""
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from sh_interfaces.action import Kontrollgang


def main(args=None):
    rclpy.init(args=args)
    knoten = Node("kontrollgang_client")
    client = ActionClient(knoten, Kontrollgang, "kontrollgang")
    if not client.wait_for_server(timeout_sec=5.0):
        knoten.get_logger().error("Action /kontrollgang nicht erreichbar")
        sys.exit(1)
    raeume = sys.argv[1:] or ["flur", "kueche", "wohnzimmer"]
    rueckmeldung = lambda f: print(  # noqa: E731
        f"  {f.feedback.raum:<12} {f.feedback.fortschritt:4.0%}")
    zukunft = client.send_goal_async(Kontrollgang.Goal(raeume=raeume),
                                     feedback_callback=rueckmeldung)
    rclpy.spin_until_future_complete(knoten, zukunft)
    ziel = zukunft.result()
    if not ziel.accepted:
        print("Ziel abgelehnt")
        sys.exit(1)
    ergebnis = ziel.get_result_async()
    rclpy.spin_until_future_complete(knoten, ergebnis)
    r = ergebnis.result().result
    print(f"{r.besucht} Räume: {r.meldung}")
    knoten.destroy_node()
    rclpy.try_shutdown()
