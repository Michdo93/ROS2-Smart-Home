"""Kapitel 12: Wie schnell kommt eine Änderung in openHAB als ROS-Nachricht an?

Setzt den Dimmer 100-mal per REST auf einen neuen Wert und misst die Zeit bis zur
Nachricht auf /openhab/items/Wohnzimmer_Dimmer/state. Läuft gegen die Brücke, die
gerade gestartet ist – Python oder C++.

    python3 latenz_messen.py [anzahl]
"""
import os
import statistics
import sys
import threading
import time

import rclpy
from openhab import Items, OpenHABClient
from openhab_msgs.msg import ItemState
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

ITEM = "Wohnzimmer_Dimmer"
QOS = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE,
                 durability=DurabilityPolicy.TRANSIENT_LOCAL)

anzahl = int(sys.argv[1]) if len(sys.argv) > 1 else 100
items = Items(OpenHABClient(os.environ["OPENHAB_URL"], token=os.environ["OPENHAB_TOKEN"]))
rclpy.init()
knoten = rclpy.create_node("latenz_messen")
gesendet, dauer = {}, []
angekommen = threading.Event()


def empfangen(m):
    t = gesendet.pop(m.state, None)
    if t is not None:
        dauer.append((time.perf_counter() - t) * 1000)
        angekommen.set()


knoten.create_subscription(ItemState, f"/openhab/items/{ITEM}/state", empfangen, QOS)
ausfuehrer = SingleThreadedExecutor()
ausfuehrer.add_node(knoten)
faden = threading.Thread(target=ausfuehrer.spin)
faden.start()
time.sleep(2)                                     # Verbindung aufbauen lassen

for i in range(anzahl):
    wert = str(10 + i % 80)
    if items.getItemState(ITEM) == wert:   # nur echte Änderungen erzeugen Ereignisse
        wert = str(int(wert) + 1)
    angekommen.clear()
    gesendet[wert] = time.perf_counter()
    items.postUpdate(ITEM, wert)
    angekommen.wait(2.0)

q = statistics.quantiles(dauer, n=100)
print(f"{len(dauer)}/{anzahl} Änderungen, Median {statistics.median(dauer):.1f} ms, "
      f"p95 {q[94]:.1f} ms, max {max(dauer):.1f} ms")
ausfuehrer.shutdown()                             # Faden sauber beenden
faden.join()
knoten.destroy_node()
rclpy.shutdown()
