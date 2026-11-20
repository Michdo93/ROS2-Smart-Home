"""Kapitel 9: Server-Sent Events – jede Zustandsänderung sofort mitbekommen.

    python3 02_ereignisse_lauschen.py      (Strg+C beendet)
"""
import os

from openhab import ItemEvents, OpenHABClient, iterSSEEvents

client = OpenHABClient(os.environ["OPENHAB_URL"], token=os.environ["OPENHAB_TOKEN"])
strom = ItemEvents(client).ItemStateChangedEvent()     # alle Items
print("warte auf Änderungen ...")
try:
    for ereignis in iterSSEEvents(strom):
        item = ereignis["topic"].split("/")[2]
        alt, neu = ereignis["payload"]["oldValue"], ereignis["payload"]["value"]
        print(f"{item:<24} {alt} -> {neu}")
except KeyboardInterrupt:
    pass
