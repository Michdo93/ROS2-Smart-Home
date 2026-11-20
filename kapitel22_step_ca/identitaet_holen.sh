#!/usr/bin/env bash
# Kapitel 22: Zertifikat einer Enclave mit einem Einmal-Token von step-ca holen
#   Auf dem Rechner mit dem Provisioner-Passwort:
#     step ca token /hand_detektor --provisioner sros2 --password-file passwort
#   Auf dem Pi, mit dem Token:
#     ./identitaet_holen.sh ~/sros2_haus /hand_detektor <token> [Dauer]
# Rechte (permissions.p7s) und governance bleiben von SROS2 – nur die Identität
# kommt von step-ca. Vorher einmal: step ca bootstrap (siehe Buch).
set -euo pipefail
KS=${1:?Schlüsselspeicher}; ENCLAVE=${2:?Enclave}; TOKEN=${3:?Token}
DAUER=${4:-24h}; D=$KS/enclaves$ENCLAVE
step ca certificate --token "$TOKEN" --not-after "$DAUER" --force \
  "$ENCLAVE" "$D/cert.pem" "$D/key.pem"
# identity_ca.cert.pem ist bei SROS2 ein Symlink auf public/ – erst entfernen,
# sonst überschreibt man die CA der Berechtigungen!
rm -f "$D/identity_ca.cert.pem"
# Fast DDS braucht Zwischen- und Wurzelzertifikat: das zweite Zertifikat in
# cert.pem ist das der Zwischen-CA, die Wurzel hat step ca bootstrap abgelegt
awk '/BEGIN CERT/{n++} n==2' "$D/cert.pem" > "$D/identity_ca.cert.pem"
cat "$(step path)/certs/root_ca.crt" >> "$D/identity_ca.cert.pem"
step certificate inspect "$D/cert.pem" --short
