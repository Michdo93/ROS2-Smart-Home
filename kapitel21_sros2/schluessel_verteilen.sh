#!/usr/bin/env bash
# Kapitel 21: jedem Rechner nur die Enclaves geben, die er braucht – ohne private/
#   ./schluessel_verteilen.sh ~/sros2_haus pi@pi-flur.local /kinect_v1/driver /hand_detektor
#   ./schluessel_verteilen.sh ~/sros2_haus pi@server.local /openhab_bridge
set -euo pipefail
KS=${1:?Schlüsselspeicher}; ZIEL=${2:?Rechner}; shift 2
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/sros2_haus/enclaves"
cp -r "$KS/public" "$TMP/sros2_haus/"                        # nur Zertifikate
cp "$KS"/enclaves/governance.* "$TMP/sros2_haus/enclaves/"
for enclave in "$@"; do
  mkdir -p "$TMP/sros2_haus/enclaves$(dirname "$enclave")"
  cp -r "$KS/enclaves$enclave" "$TMP/sros2_haus/enclaves$enclave"
done
chmod -R go-rwx "$TMP/sros2_haus"
if [[ $ZIEL == *@* ]]; then                                  # user@rechner
  rsync -a --delete "$TMP/sros2_haus/" "$ZIEL:sros2_haus/"
else
  mkdir -p "$ZIEL" && cp -r "$TMP/sros2_haus/." "$ZIEL/"   # lokaler Ordner
fi
echo "verteilt nach $ZIEL: $*"
