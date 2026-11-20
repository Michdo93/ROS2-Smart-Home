"""Kapitel 6: Action-Server – ein (simulierter) Roboter fährt Räume ab.

Jeder Raum dauert zwei Sekunden; Rückmeldung nach jedem Raum, abbrechbar.

    ros2 run sh_grundlagen kontrollgang_server
"""
import time

import rclpy
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from sh_interfaces.action import Kontrollgang


class KontrollgangServer(Node):
    def __init__(self):
        super().__init__("kontrollgang_server")
        self.dauer = self.declare_parameter("sekunden_pro_raum", 2.0).value
        # Reentrant: Abbruchanfragen dürfen parallel zum laufenden Auftrag ankommen
        ActionServer(self, Kontrollgang, "kontrollgang", self.ausfuehren,
                     cancel_callback=lambda _ziel: CancelResponse.ACCEPT,
                     callback_group=ReentrantCallbackGroup())

    def ausfuehren(self, ziel):
        raeume = list(ziel.request.raeume)
        ergebnis = Kontrollgang.Result()
        for i, raum in enumerate(raeume, 1):
            if ziel.is_cancel_requested:
                ziel.canceled()
                ergebnis.besucht, ergebnis.meldung = i - 1, "abgebrochen"
                return ergebnis
            time.sleep(self.dauer)                       # "fahren"
            ziel.publish_feedback(Kontrollgang.Feedback(raum=raum,
                                                        fortschritt=i / len(raeume)))
            self.get_logger().info(f"{raum} erreicht ({i}/{len(raeume)})")
        ziel.succeed()
        ergebnis.besucht, ergebnis.meldung = len(raeume), "alle Räume kontrolliert"
        return ergebnis


def main(args=None):
    rclpy.init(args=args)
    knoten = KontrollgangServer()
    try:
        rclpy.spin(knoten, executor=MultiThreadedExecutor())  # Abbruch während der Fahrt
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
