"""Kapitel 14: Roboter und Haus in beide Richtungen – über die openHAB-Brücke.

  openHAB -> Roboter  Befehl  Roboter_Ziel (String)        "kueche", "wohnzimmer", ...
  openHAB -> Roboter  Zustand Diele_Praesenz (Switch)      ist jemand da, wartet er
  Roboter -> openHAB  Befehl  Wohnzimmer_Deckenlampe_Schalter  Licht an, solange er
                                                           im Wohnzimmer ist
  Roboter -> openHAB  Zustand Roboter_Status, Roboter_Raum, Roboter_X, Roboter_Y,
                              Roboter_Akku

    ros2 launch sh_szenarien roboter.launch.py
"""
import math

import rclpy
from geometry_msgs.msg import Twist
from openhab_msgs.msg import ItemCommand, ItemState
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from turtlesim.msg import Pose

from .turtle_kontrollgang import RAEUME

ZUSTAND = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                     durability=DurabilityPolicy.TRANSIENT_LOCAL)
LICHT = {"wohnzimmer": "Wohnzimmer_Deckenlampe_Schalter"}   # Raum -> Licht-Item


class HausRoboter(Node):
    def __init__(self):
        super().__init__("haus_roboter")
        self.pose, self.ziel, self.raum = None, None, None
        self.anwesend = False
        self.akku, self.gemeldet = 100.0, {}
        self.fahren = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        self.an_openhab = self.create_publisher(ItemCommand, "/openhab/command", 10)
        self.create_subscription(Pose, "/turtle1/pose", self.neue_pose, 10)
        # Befehl und Zustand aus openHAB – beide kommen als ItemState
        self.create_subscription(ItemState, "/openhab/items/Roboter_Ziel/state",
                                 self.neues_ziel, ZUSTAND)
        self.create_subscription(ItemState, "/openhab/items/Diele_Praesenz/state",
                                 self.praesenz, ZUSTAND)
        self.create_timer(0.1, self.regeln)       # fahren: 10-mal pro Sekunde
        self.create_timer(1.0, self.melden)       # openHAB: einmal pro Sekunde

    # ------------------------------------------------------------ openHAB -> Roboter
    def neues_ziel(self, m):
        ziel = m.state.lower()
        if ziel in RAEUME and ziel != self.ziel:
            self.ziel = ziel
            self.get_logger().info(f"neues Ziel aus openHAB: {ziel}")

    def praesenz(self, m):
        anwesend = m.has_number and m.number > 0
        if anwesend != self.anwesend:
            self.anwesend = anwesend
            self.get_logger().info("Anwesenheit -> warten" if anwesend
                                   else "niemand da -> weiterfahren")

    # ------------------------------------------------------------ Roboter -> openHAB
    def an(self, item, wert, update=True):
        """update=True: Zustand melden, False: Befehl an ein Gerät"""
        msg = ItemCommand(name=item, command=str(wert), update=update)
        self.an_openhab.publish(msg)

    def melden(self):
        if self.pose is None:
            return
        werte = {"Roboter_X": f"{self.pose.x:.1f} m",
                 "Roboter_Y": f"{self.pose.y:.1f} m",
                 "Roboter_Akku": f"{self.akku:.0f} %",
                 "Roboter_Status": self.status()}
        for item, wert in werte.items():
            if self.gemeldet.get(item) != wert:   # nur Änderungen schicken
                self.an(item, wert)
                self.gemeldet[item] = wert

    def status(self):
        if self.ziel is None:
            return f"steht in {self.raum or 'unbekannt'}"
        return f"wartet vor {self.ziel}" if self.anwesend else f"fährt zu {self.ziel}"

    def raum_gewechselt(self, neu):
        alt, self.raum = self.raum, neu
        self.an("Roboter_Raum", neu or "unterwegs")
        if alt in LICHT:
            self.an(LICHT[alt], "OFF", update=False)    # Befehl: Licht aus
        if neu in LICHT:
            self.an(LICHT[neu], "ON", update=False)     # Befehl: Licht an
        self.get_logger().info(f"Raum: {alt or 'unterwegs'} -> {neu or 'unterwegs'}")

    # ------------------------------------------------------------ fahren
    def neue_pose(self, p):
        self.pose = p
        raum = next((r for r, (x, y) in RAEUME.items()
                     if math.hypot(x - p.x, y - p.y) < 0.4), None)
        if raum != self.raum:
            self.raum_gewechselt(raum)

    def regeln(self):
        if self.pose is None or self.ziel is None or self.anwesend:
            self.fahren.publish(Twist())              # stehen bleiben
            return
        x, y = RAEUME[self.ziel]
        abstand = math.hypot(x - self.pose.x, y - self.pose.y)
        if abstand < 0.1:
            self.get_logger().info(f"angekommen: {self.ziel}")
            self.ziel = None
            self.fahren.publish(Twist())
            return
        fehler = math.atan2(y - self.pose.y, x - self.pose.x) - self.pose.theta
        fehler = math.atan2(math.sin(fehler), math.cos(fehler))
        t = Twist()
        t.angular.z = 4.0 * fehler
        t.linear.x = min(2.0, 1.5 * abstand) if abs(fehler) < 0.3 else 0.0
        self.akku = max(0.0, self.akku - 0.02 * t.linear.x)
        self.fahren.publish(t)


def main(args=None):
    rclpy.init(args=args)
    knoten = HausRoboter()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
