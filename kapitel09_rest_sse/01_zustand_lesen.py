"""Kapitel 9: Zustand und Typ eines Items über die REST API lesen."""
import os

from openhab import Items, OpenHABClient

client = OpenHABClient(os.environ["OPENHAB_URL"], token=os.environ["OPENHAB_TOKEN"])
items = Items(client)

for name in ("Flur_Licht", "Wohnzimmer_Dimmer", "Wohnzimmer_Temperatur"):
    item = items.getItem(name)
    print(f"{name:<24} {item['type']:<20} {item['state']}")
