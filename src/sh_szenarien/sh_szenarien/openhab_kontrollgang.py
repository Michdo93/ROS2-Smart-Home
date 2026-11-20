"""Kapitel 14: ein Schalter in openHAB startet eine ROS-2-Action.

Roboter_Kontrollgang ON  ->  Action /kontrollgang  ->  Rückmeldungen in Roboter_Status
Am Ende schaltet der Knoten Roboter_Kontrollgang wieder auf OFF; OFF während der Fahrt
bricht ab.

    ros2 run sh_szenarien openhab_kontrollgang --ros-args -p raeume:="[flur, kueche, bad]"
"""
import rclpy
from openhab_msgs.msg import ItemCommand, ItemState
from rclpy.action import ActionClient
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from sh_interfaces.action import Kontrollgang

ZUSTAND = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)


class OpenHABKontrollgang(Node):
    def __init__(self):
        super().__init__("openhab_kontrollgang")
        self.raeume = self.declare_parameter(
            "raeume", ["flur", "kueche", "wohnzimmer", "schlafzimmer", "bad"]).value
        self.befehl = self.create_publisher(ItemCommand, "/openhab/command", 10)
        self.action = ActionClient(self, Kontrollgang, "kontrollgang")
        self.ziel = None
        self.create_subscription(ItemState, "/openhab/items/Roboter_Kontrollgang/state",
                                 self.schalter, ZUSTAND)

    def openhab(self, item, wert, update=True):
        self.befehl.publish(ItemCommand(name=item, command=wert, update=update))

    def schalter(self, m):
        if m.state == "ON" and self.ziel is None:
            if not self.action.wait_for_server(timeout_sec=2.0):
                self.openhab("Roboter_Status", "kein Roboter erreichbar")
                self.openhab("Roboter_Kontrollgang", "OFF", update=False)
                return
            self.openhab("Roboter_Status", "startet")
            zukunft = self.action.send_goal_async(Kontrollgang.Goal(raeume=self.raeume),
                                                  feedback_callback=self.rueckmeldung)
            zukunft.add_done_callback(self.angenommen)
            self.ziel = zukunft
        elif m.state == "OFF" and hasattr(self.ziel, "cancel_goal_async"):
            self.ziel.cancel_goal_async()                # Abbruch aus openHAB

    def angenommen(self, zukunft):
        handle = zukunft.result()
        if not handle.accepted:
            self.openhab("Roboter_Status", "abgelehnt")
            self.ziel = None
            return
        self.ziel = handle
        handle.get_result_async().add_done_callback(self.fertig)

    def rueckmeldung(self, f):
        self.openhab("Roboter_Status",
                     f"{f.feedback.raum} ({f.feedback.fortschritt:.0%})")

    def fertig(self, zukunft):
        r = zukunft.result().result
        self.openhab("Roboter_Status",
                     f"{r.meldung} ({r.besucht} von {len(self.raeume)} Räumen)")
        self.openhab("Roboter_Kontrollgang", "OFF", update=False)
        self.ziel = None


def main(args=None):
    rclpy.init(args=args)
    knoten = OpenHABKontrollgang()
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
