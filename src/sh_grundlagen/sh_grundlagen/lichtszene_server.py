"""Kapitel 5: Service-Server – schaltet eine Lichtszene.

Die Befehle gehen auf die Topics der openHAB-Brücke (Kapitel 10). Läuft keine Brücke,
sieht man sie mit: ros2 topic echo /openhab/items/Wohnzimmer_Licht/command

    ros2 run sh_grundlagen lichtszene_server
"""
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sh_interfaces.srv import LichtSzene
from std_msgs.msg import String

SZENEN = {  # Szene -> Item -> Command
    "lesen": {"Licht": "ON", "Dimmer": "80"},
    "kino": {"Licht": "OFF", "Dimmer": "15"},
    "aus": {"Licht": "OFF", "Dimmer": "0"},
}


class LichtSzeneServer(Node):
    def __init__(self):
        super().__init__("lichtszene_server")
        self.pubs = {}
        self.create_service(LichtSzene, "lichtszene", self.schalten)

    def befehl(self, item, command):
        if item not in self.pubs:
            thema = f"/openhab/items/{item}/command"
            self.pubs[item] = self.create_publisher(String, thema, 10)
        self.pubs[item].publish(String(data=command))

    def schalten(self, anfrage, antwort):
        szene = SZENEN.get(anfrage.szene)
        if szene is None:
            antwort.erfolg = False
            antwort.meldung = f"unbekannte Szene, bekannt sind: {', '.join(SZENEN)}"
            return antwort
        raum = anfrage.raum.capitalize()                 # wohnzimmer -> Wohnzimmer
        for geraet, command in szene.items():
            self.befehl(f"{raum}_{geraet}", command)
        antwort.erfolg = True
        antwort.meldung = f"{raum}: Szene {anfrage.szene}"
        self.get_logger().info(antwort.meldung)
        return antwort


def main(args=None):
    rclpy.init(args=args)
    knoten = LichtSzeneServer()
    try:
        rclpy.spin(knoten)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        knoten.destroy_node()
        rclpy.try_shutdown()
