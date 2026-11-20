#!/usr/bin/env bash
# Kapitel 21: SROS2 – Schlüsselspeicher, Enclaves und Rechte für "Hand erkannt"
#   ./sicherheit_einrichten.sh [~/sros2_haus]
set -euo pipefail
KS=${1:-$HOME/sros2_haus}
# Governance und Berechtigungen gelten nur für diese Domain – dieselbe wie im Haus!
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-7}
echo "Domain: $ROS_DOMAIN_ID"
DIR=$(cd "$(dirname "$0")" && pwd)
ros2 security create_keystore "$KS"
ENCLAVES="/kinect_v1/driver /kinect_v2/driver /hand_detektor /openhab_bridge
          /mqtt_client /werkzeuge"
for enclave in $ENCLAVES; do
  ros2 security create_enclave "$KS" "$enclave"
done
# Berechtigungen aus der Richtlinie (statt "alles erlaubt") erzeugen und signieren
for enclave in $ENCLAVES; do
  ros2 security create_permission "$KS" "$enclave" "$DIR/richtlinie_hand.xml"
done
cat <<INFO

Schlüsselspeicher: $KS
Für jedes Terminal bzw. jeden Dienst:
  export ROS_SECURITY_KEYSTORE=$KS
  export ROS_SECURITY_ENABLE=true
  export ROS_SECURITY_STRATEGY=Enforce
Start mit Enclave, z. B.:
  ros2 run sh_hand hand_detektor --ros-args --enclave /hand_detektor
INFO
