# ROS2-Smart-Home

Begleit-Repository zum Buch **Smart Home & ROS2 – Vernetzen Sie Ihr Zuhause wie einen Roboter**
von Michael Christian Dörflinger (Praxisreihe Smart Home). Es enthält alle Codes des Buchs,
nach Kapiteln geordnet. Jede Datei, die im Buch abgedruckt ist, liegt hier genau so.

Getestet mit ROS 2 **Lyrical Luth** (Ubuntu 26.04) und **Jazzy Jalisco** (Ubuntu 24.04,
Raspberry Pi 4/5) gegen openHAB 5.

## Weitere Repositorys zum Buch

| Repository | Inhalt | Kapitel |
|---|---|---|
| [ros2_openhab_ws](https://github.com/Michdo93/ros2_openhab_ws) | openHAB-Brücke (Python und C++), `openhab_msgs` | 10–14, 19 |
| [openHAB-Virtual-Smart-Home](https://github.com/Michdo93/openHAB-Virtual-Smart-Home) | virtuelles Haus: Items aller Typen, Regeln, Sitemap | 11, 14 |
| [ROS2-Kinect-v1-Xbox-360](https://github.com/Michdo93/ROS2-Kinect-v1-Xbox-360) | Treiber Kinect v1, Simulation | 16, 18, 19 |
| [ROS2-Kinect-v2-Xbox-One](https://github.com/Michdo93/ROS2-Kinect-v2-Xbox-One) | Treiber Kinect v2, Simulation | 17, 18 |
| [mqtt_client](https://github.com/ika-rwth-aachen/mqtt_client) (ika, RWTH Aachen) | MQTT-Brücke für ROS 2, als Paket `ros-<distro>-mqtt-client` | 2 |

## Voraussetzungen

* Ubuntu 26.04 mit ROS 2 Lyrical oder Ubuntu 24.04 mit Jazzy – das Skript aus Kapitel 4
  installiert beides: `kapitel04_installation/ros2_installieren.sh`
* für Kapitel 2: Mosquitto und Home Assistant oder openHAB mit MQTT-Binding
* openHAB 5 mit den Items aus `openhab-conf/` und dem virtuellen Haus (ab Kapitel 9)
* Kinect v1 oder v2 – **nicht nötig**: alle Kamerabeispiele laufen mit `simulate:=true`

## Installation

```bash
git clone https://github.com/Michdo93/ROS2-Smart-Home.git
ROS2-Smart-Home/kapitel04_installation/workspace_einrichten.sh   # legt ~/ros2_ws an und baut
source ~/ros2_ws/install/setup.bash
cp ~/ros2_ws/src/ROS2-Smart-Home/.env.example ~/ros2_ws/.env     # Adresse und Token eintragen
set -a; . ~/ros2_ws/.env; set +a
```

Die Konfiguration für openHAB: die Ordner unter `openhab-conf/` (items, things, rules,
sitemaps, transform) in die gleichnamigen Ordner von `$OPENHAB_CONF/` kopieren, dazu das
virtuelle Haus aus [openHAB-Virtual-Smart-Home](https://github.com/Michdo93/openHAB-Virtual-Smart-Home).
Für Home Assistant liegt in `homeassistant/` ein Paket (`packages:` in der `configuration.yaml`).

## Inhalt

| Kapitel | Ordner / Paket | Inhalt |
|---|---|---|
| 2 | `src/sh_mqtt/`, `homeassistant/`, `openhab-conf/things/mqtt.things` | ROS 2 über MQTT mit Home Assistant und openHAB: Zustände und Befehle in beide Richtungen, turtlesim |
| 4 | `kapitel04_installation/` | ROS 2 installieren, Workspace mit allen Repos |
| 5 | `src/sh_interfaces/`, `src/sh_grundlagen/`, `src/sh_grundlagen_cpp/` | eigene Nachricht `Raumklima`, Publisher und Subscriber in Python und C++ |
| 6 | `src/sh_grundlagen/` | Service `LichtSzene`, Action `Kontrollgang`, Parameter zur Laufzeit |
| 7 | `src/sh_grundlagen/` | `qos_demo`: volatile und transient local |
| 8 | `src/sh_grundlagen/launch/haus.launch.py` | drei Räume mit Namespaces und Remapping |
| 9 | `kapitel09_rest_sse/` | REST API und Server-Sent Events mit python-openhab-rest-client |
| 11 | `kapitel11_bruecke/` | Konfigurationen der Brücke, `alle_typen.py`: jeder Item- und Befehlstyp |
| 12 | `kapitel12_vergleich/` | Laufzeit und Speicher von Python- und C++-Brücke messen |
| 13 | `src/sh_szenarien/` | Präsenz und Licht, Aufzeichnung mit rosbag2 |
| 14 | `src/sh_szenarien/` | Roboter und Haus in beide Richtungen, Kontrollgang als Action |
| 15, 16, 18 | `src/sh_kamera/` | Bilder in NumPy umwandeln, Tag/Nacht-Umschaltung der Kinect über openHAB, Abstand, Synchronisieren, Punktwolke, Bandbreite messen, JPEG-Kompression, Bewegungserkennung, Vergleich mit ZeroMQ, viele Anwendungen an einer Kamera |
| 19 | `src/sh_hand/` | Projekt „Hand erkannt“: Kinect → ROS 2 → openHAB oder Home Assistant |
| 20 | `kapitel20_verteilt/` | gemeinsame Umgebung, systemd-Dienste für Pi und Brücke |
| 21 | `kapitel21_sros2/` | Schlüsselspeicher, Enclaves, Richtlinie für „Hand erkannt“ |
| – | `openhab-conf/` | Items, Things, Regeln, Sitemaps und Transformationen, die die Beispiele voraussetzen |

## Schnellstart ohne Hardware

```bash
ros2 launch sh_mqtt mqtt.launch.py                                # Kapitel 2, mit MQTT
ros2 run sh_grundlagen qos_demo                                   # Kapitel 7
ros2 launch sh_grundlagen haus.launch.py                          # Kapitel 8
ros2 launch sh_kamera viele_anwendungen.launch.py simulate:=true  # Kapitel 18
ros2 launch sh_hand hand.launch.py simulate:=true                 # Kapitel 19, mit openHAB
ros2 launch sh_hand hand.launch.py simulate:=true ziel:=mqtt      # Kapitel 19, Home Assistant
```

## Lizenz

MIT
