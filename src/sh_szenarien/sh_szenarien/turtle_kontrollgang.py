"""Kapitel 14: Action-Server mit "echtem" Roboter – die turtlesim-Schildkröte
fährt die Räume ab.

    ros2 run turtlesim turtlesim_node
    ros2 run sh_szenarien turtle_kontrollgang
"""
import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.action import ActionServer, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from sh_interfaces.action import Kontrollgang
from turtlesim.msg import Pose

# Grundriss im turtlesim-Fenster (0 ... 11 m)
RAEUME = {"flur": (5.5, 5.5), "kueche": (2.0, 9.0), "wohnzimmer": (9.0, 9.0),
          "bad": (2.0, 2.0), "schlafzimmer": (9.0, 2.0)}


class TurtleKontrollgang(Node):
    def __init__(self):
        super().__init__("turtle_kontrollgang")
        gruppe = ReentrantCallbackGroup()
        self.pose = None
        self.create_subscription(Pose, "/turtle1/pose", self.neue_pose, 10,
                                 callback_group=gruppe)
        self.fahren = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        ActionServer(self, Kontrollgang, "kontrollgang", self.ausfuehren,
                     cancel_callback=lambda _z: CancelResponse.ACCEPT,
                     callback_group=gruppe)

    def neue_pose(self, p):
        self.pose = p

    def fahre_zu(self, ziel, x, y):
        """Einfacher P-Regler: erst drehen, dann fahren. False bei Abbruch."""
        while rclpy.ok():
            if ziel.is_cancel_requested:
                return False
            if self.pose is None:
                time.sleep(0.05)
                continue
            dx, dy = x - self.pose.x, y - self.pose.y
            abstand = math.hypot(dx, dy)
            if abstand < 0.1:
                self.fahren.publish(Twist())
                return True
            fehler = math.atan2(dy, dx) - self.pose.theta
            fehler = math.atan2(math.sin(fehler), math.cos(fehler))  # -pi ... pi
            t = Twist()
            t.angular.z = 4.0 * fehler
            t.linear.x = min(2.0, 1.5 * abstand) if abs(fehler) < 0.3 else 0.0
            self.fahren.publish(t)
            time.sleep(0.05)
        return False

    def ausfuehren(self, ziel):
        raeume = [r for r in ziel.request.raeume if r in RAEUME]
        ergebnis = Kontrollgang.Result()
        for i, raum in enumerate(raeume, 1):
            if not self.fahre_zu(ziel, *RAEUME[raum]):
                ziel.canceled()
                ergebnis.besucht, ergebnis.meldung = i - 1, "abgebrochen"
                return ergebnis
            ziel.publish_feedback(Kontrollgang.Feedback(raum=raum,
                                                        fortschritt=i / len(raeume)))
            self.get_logger().info(f"{raum} erreicht")
        ziel.succeed()
        unbekannt = len(ziel.request.raeume) - len(raeume)
        ergebnis.besucht = len(raeume)
        ergebnis.meldung = "alle Räume kontrolliert" + \
            (f", {unbekannt} unbekannt" if unbekannt else "")
        return ergebnis


def main(args=None):
    rclpy.init(args=args)
    knoten = TurtleKontrollgang()
    try:
        rclpy.spin(knoten, executor=MultiThreadedExecutor())
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
