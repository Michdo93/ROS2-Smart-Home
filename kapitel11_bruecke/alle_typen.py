"""Kapitel 11: Jeder Item-Typ, jeder Befehlstyp – über die Brücke an openHAB.

Schickt Befehle (command) und Updates (update) an Items aus dem virtuellen Haus
(github.com/Michdo93/openHAB-Virtual-Smart-Home) und zeigt, was die Brücke danach
als ItemState liefert. Die Brücke muss laufen.

    python3 alle_typen.py
"""
import time

import rclpy
from openhab_msgs.srv import GetItem, SendCommand

# (Item, Wert, "command" oder "update")
FAELLE = [
    ("Wohnzimmer_Steckdose_Schalter", "ON", "command"),       # OnOffType
    ("Wohnzimmer_Steckdose_Schalter", "UP", "command"),       # falscher Typ
    ("Wohnzimmer_Deckenlampe_Helligkeit", "40", "command"),   # PercentType
    ("Wohnzimmer_Deckenlampe_Helligkeit", "12.5", "command"),
    ("Wohnzimmer_Deckenlampe_Helligkeit", "INCREASE", "command"),  # IncreaseDecrease
    ("Wohnzimmer_Deckenlampe_Helligkeit", "OFF", "command"),  # OnOffType
    ("Wohnzimmer_Farblampe_Farbe", "120,100,50", "command"),  # HSBType
    ("Wohnzimmer_Farblampe_Farbe", "30", "command"),          # PercentType
    ("Wohnzimmer_Farblampe_Farbe", "OFF", "command"),
    ("Wohnzimmer_Fenster_Kontakt", "CLOSED", "update"),       # OpenClosedType
    ("Wohnzimmer_Fenster_Kontakt", "OPEN", "command"),        # Contact: kein Befehl
    ("Wohnzimmer_Fenster_Kontakt", "OPEN", "update"),
    ("Wohnzimmer_Fernseher_Kanal", "7", "command"),        # DecimalType, ganz
    ("Technik_Waermepumpe_COP", "3.75", "update"),            # DecimalType, Komma
    ("Wohnzimmer_Thermostat_Soll", "21.5", "command"),        # ohne Einheit
    ("Wohnzimmer_Thermostat_Soll", "70 °F", "command"),       # QuantityType
    ("Wohnzimmer_Thermostat_Soll", "3 m", "command"),         # falsche Dimension
    ("Technik_PV_Leistung", "3.2 kW", "update"),              # wird zu W
    ("Garage_Auto_Ladestand", "80 %", "update"),              # Dimensionless
    ("Wohnzimmer_Raumluft_CO2", "900 ppm", "update"),
    ("Wohnzimmer_Rollladen_Position", "50", "command"),       # PercentType (5 s)
    ("Wohnzimmer_Rollladen_Position", "UP", "command"),       # UpDownType
    ("Wohnzimmer_Rollladen_Position", "STOP", "command"),     # StopMoveType
    ("Wohnzimmer_Soundsystem_Player", "PLAY", "command"),     # PlayPauseType
    ("Wohnzimmer_Soundsystem_Player", "NEXT", "command"),     # NextPreviousType
    ("Wohnzimmer_Soundsystem_Player", "FASTFORWARD", "command"),  # RewindFastforward
    ("Kueche_Backofen_Modus", "Grill", "command"),            # StringType
    ("Kueche_Backofen_Ende", "2026-11-20T18:30:00", "command"),  # DateTime
    ("Garage_Auto_Position", "48.051,8.207,860", "command"),  # PointType
    ("Diele_Klingel_Anruf", "Wohnung,Haustür", "update"),     # StringListType
    ("Diele_Klingel_Anruf", "Wohnung,Garten", "command"),     # Call: kein Befehl
    ("gVH_Lichter", "OFF", "command"),                        # an alle Mitglieder
    ("Haus_Saugroboter_Karte", None, None),                   # Image: nur lesen
]


def aufruf(knoten, client, anfrage):
    zukunft = client.call_async(anfrage)
    rclpy.spin_until_future_complete(knoten, zukunft)
    return zukunft.result()


def main():
    rclpy.init()
    knoten = rclpy.create_node("alle_typen")
    senden = knoten.create_client(SendCommand, "/openhab/send_command")
    lesen = knoten.create_client(GetItem, "/openhab/get_item")
    senden.wait_for_service()
    for item, wert, art in FAELLE:
        if wert is not None:
            antwort = aufruf(knoten, senden, SendCommand.Request(
                name=item, command=wert, update=(art == "update")))
            # Regeln Zeit lassen; der Rollladen fährt 10 % pro Sekunde
            time.sleep(5.5 if wert == "50" else 1.2)
            ergebnis = "ok" if antwort.success else "FEHLER"
        else:
            art, wert, ergebnis = "-", "-", "-"
        z = aufruf(knoten, lesen, GetItem.Request(name=item)).item
        zustand = z.state if len(z.state) < 30 else z.state[:26] + "..."
        zahl = f"{z.number:g} {z.unit}".strip() if z.has_number else "-"
        werte = ",".join(f"{v:g}" for v in z.values)
        print(f"{z.type:<20} {art:<7} {wert:<19} {ergebnis:<6} {zustand:<29} "
              f"{zahl:<10} {werte}")
    rclpy.shutdown()


if __name__ == "__main__":
    main()
