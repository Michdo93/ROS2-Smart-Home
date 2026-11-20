#!/usr/bin/env bash
# Kapitel 21: SROS2 – Schlüsselspeicher, Enclaves und Berechtigungen für "Hand erkannt"
#   ./sicherheit_einrichten.sh [~/sros2_haus]
set -euo pipefail
KS=${1:-$HOME/sros2_haus}
DIR=$(cd "$(dirname "$0")" && pwd)
ros2 security create_keystore "$KS"
for enclave in /kinect_v1/driver /hand_detektor /openhab_bridge; do
  ros2 security create_enclave "$KS" "$enclave"
done
# Berechtigungen aus der Richtlinie (statt "alles erlaubt") erzeugen und signieren
for enclave in /kinect_v1/driver /hand_detektor /openhab_bridge; do
  ros2 security create_permission "$KS" "$enclave" "$DIR/richtlinie_hand.xml"
done
cat <<INFO

Schlüsselspeicher: $KS
Für jedes Terminal bzw. jeden Dienst:
  export ROS_SECURITY_KEYSTORE=$KS
  export ROS_SECURITY_ENABLE=true
  export ROS_SECURITY_STRATEGY=Enforce      # Permissive: ohne passende Enclave unverschlüsselt
Start mit Enclave, z. B.:
  ros2 run sh_hand hand_detektor --ros-args --enclave /hand_detektor
INFO
