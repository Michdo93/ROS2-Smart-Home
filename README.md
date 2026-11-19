# ROS2-Smart-Home

Begleit-Repository zum Buch **Smart Home & ROS2 – Vernetzen Sie Ihr Zuhause wie einen Roboter**
von Michael Christian Dörflinger (Praxisreihe Smart Home). Es enthält alle Codes des Buchs,
nach Kapiteln geordnet. Jede Datei, die im Buch abgedruckt ist, liegt hier genau so.

Getestet mit ROS 2 **Lyrical Luth** (Ubuntu 26.04) und **Jazzy Jalisco** (Ubuntu 24.04,
Raspberry Pi 4/5) gegen openHAB 5.

## Weitere Repositorys zum Buch

| Repository | Inhalt | Kapitel |
|---|---|---|
| [ros2_openhab_ws](https://github.com/Michdo93/ros2_openhab_ws) | openHAB-Brücke (Python und C++), `openhab_msgs` | 9–12, 17 |
| [ROS2-Kinect-v1-Xbox-360](https://github.com/Michdo93/ROS2-Kinect-v1-Xbox-360) | Treiber Kinect v1, Simulation | 14, 16, 17 |
| [ROS2-Kinect-v2-Xbox-One](https://github.com/Michdo93/ROS2-Kinect-v2-Xbox-One) | Treiber Kinect v2, Simulation | 15, 16 |

## Voraussetzungen

* Ubuntu 26.04 mit ROS 2 Lyrical oder Ubuntu 24.04 mit Jazzy – das Skript aus Kapitel 3
  installiert beides: `kapitel03_installation/ros2_installieren.sh`
* openHAB 5 mit den Items aus `openhab-conf/` (ab Kapitel 8)
* Kinect v1 oder v2 – **nicht nötig**: alle Kamerabeispiele laufen mit `simulate:=true`

## Installation

```bash
git clone https://github.com/Michdo93/ROS2-Smart-Home.git
ROS2-Smart-Home/kapitel03_installation/workspace_einrichten.sh   # legt ~/ros2_ws an und baut
source ~/ros2_ws/install/setup.bash
cp ~/ros2_ws/src/ROS2-Smart-Home/.env.example ~/ros2_ws/.env     # Adresse und Token eintragen
set -a; . ~/ros2_ws/.env; set +a
```

Die Konfiguration für openHAB: `openhab-conf/items/ros2.items` nach `$OPENHAB_CONF/items/`,
`openhab-conf/rules/hand.rules` nach `$OPENHAB_CONF/rules/`.

## Inhalt

| Kapitel | Ordner / Paket | Inhalt |
|---|---|---|
| 3 | `kapitel03_installation/` | ROS 2 installieren, Workspace mit allen Repos |
| 4 | `src/sh_interfaces/`, `src/sh_grundlagen/`, `src/sh_grundlagen_cpp/` | eigene Nachricht `Raumklima`, Publisher und Subscriber in Python und C++ |
| 5 | `src/sh_grundlagen/` | Service `LichtSzene`, Action `Kontrollgang`, Parameter zur Laufzeit |
| 6 | `src/sh_grundlagen/` | `qos_demo`: volatile und transient local |
| 7 | `src/sh_grundlagen/launch/haus.launch.py` | drei Räume mit Namespaces und Remapping |
| 8 | `kapitel08_rest_sse/` | REST API und Server-Sent Events mit python-openhab-rest-client |
| 10 | `kapitel10_bruecke/` | Konfigurationen der Brücke: Items, Gruppe, Tags, ROS-Eingänge |
| 11 | `kapitel11_vergleich/` | Laufzeit und Speicher von Python- und C++-Brücke messen |
| 12 | `src/sh_szenarien/` | openHAB-Schalter startet eine Action, turtlesim-Roboter, Aufzeichnung mit rosbag2 |
| 13, 14, 16 | `src/sh_kamera/` | Bilder in NumPy umwandeln, Tag/Nacht-Umschaltung der Kinect über openHAB, Abstand, Synchronisieren, Punktwolke, Bandbreite messen, JPEG-Kompression, Bewegungserkennung, Vergleich mit ZeroMQ, viele Anwendungen an einer Kamera |
| 17 | `src/sh_hand/` | Projekt „Hand erkannt“: Kinect → ROS 2 → openHAB |
| 18 | `kapitel18_verteilt/` | gemeinsame Umgebung, systemd-Dienste für Pi und Brücke |
| 19 | `kapitel19_sros2/` | Schlüsselspeicher, Enclaves, Richtlinie für „Hand erkannt“ |
| – | `openhab-conf/` | Items und Regeln, die die Beispiele voraussetzen |

## Schnellstart ohne Hardware

```bash
ros2 run sh_grundlagen qos_demo                                   # Kapitel 6
ros2 launch sh_grundlagen haus.launch.py                          # Kapitel 7
ros2 launch sh_kamera viele_anwendungen.launch.py simulate:=true  # Kapitel 16
ros2 launch sh_hand hand.launch.py simulate:=true                 # Kapitel 17, mit openHAB
```

## Lizenz

MIT
