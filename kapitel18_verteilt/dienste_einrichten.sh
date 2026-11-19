#!/usr/bin/env bash
# Kapitel 18: Umgebung und Dienste auf einem Rechner einrichten
#   sudo ./dienste_einrichten.sh kinect     # Raspberry Pi mit Kinect
#   sudo ./dienste_einrichten.sh bruecke    # Rechner mit der openHAB-Brücke
set -euo pipefail
ROLLE=${1:?kinect oder bruecke}
DIR=$(cd "$(dirname "$0")" && pwd)
install -d -m 755 /etc/ros2
install -m 644 "$DIR/ros2-umgebung.conf" /etc/ros2/ros2-umgebung.conf
if [ "$ROLLE" = bruecke ]; then
  if [ ! -f /etc/ros2/openhab-token.conf ]; then
    read -rsp "openHAB-API-Token: " TOKEN; echo
    install -m 600 /dev/null /etc/ros2/openhab-token.conf
    echo "OPENHAB_TOKEN=$TOKEN" > /etc/ros2/openhab-token.conf
  fi
  install -m 644 "$DIR/../kapitel10_bruecke/bruecke_gruppe.yaml" /etc/ros2/bruecke.yaml
fi
install -m 644 "$DIR/ros2-$ROLLE.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now "ros2-$ROLLE"
systemctl --no-pager status "ros2-$ROLLE" | head -5
