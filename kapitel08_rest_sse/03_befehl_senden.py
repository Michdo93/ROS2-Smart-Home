"""Kapitel 8: Command senden und den neuen Zustand prüfen."""
import os
import time

from openhab import Items, OpenHABClient

client = OpenHABClient(os.environ["OPENHAB_URL"], token=os.environ["OPENHAB_TOKEN"])
items = Items(client)

items.sendCommand("Wohnzimmer_Dimmer", "40", "kapitel08")   # Quelle sieht man im Log
time.sleep(0.5)
print("Wohnzimmer_Dimmer =", items.getItemState("Wohnzimmer_Dimmer"))
