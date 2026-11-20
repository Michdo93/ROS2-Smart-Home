#!/usr/bin/env bash
# Kapitel 22: Zertifikate der Enclaves eines Dienstes laufend erneuern und den
# Dienst danach neu starten (ein Knoten liest sein Zertifikat nur beim Start).
#   erneuern.sh <Schlüsselspeicher> <Dienst> <Enclave> [<Enclave> ...]
#   erneuern.sh /home/pi/sros2_haus ros2-kinect /kinect_v1/driver
set -euo pipefail
KS=${1:?Schlüsselspeicher}; DIENST=${2:?Dienst}; shift 2
for enclave in "$@"; do
  D=$KS/enclaves$enclave
  # erneuert, wenn 2/3 der Laufzeit vorbei sind – bei 24 h also nach 16 h
  step ca renew --daemon --force --exec "systemctl restart $DIENST" \
    "$D/cert.pem" "$D/key.pem" &
done
wait -n    # endet ein Daemon, endet das Skript – systemd startet es neu
