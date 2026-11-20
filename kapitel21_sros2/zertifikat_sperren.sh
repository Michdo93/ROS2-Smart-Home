#!/usr/bin/env bash
# Kapitel 21: das Zertifikat einer Enclave sperren und die Sperrliste verteilen
#   ./zertifikat_sperren.sh ~/sros2_haus /hand_detektor
# Danach den Schlüsselspeicher mit schluessel_verteilen.sh neu verteilen.
set -euo pipefail
KS=${1:?Schlüsselspeicher}; ENCLAVE=${2:?Enclave}
DB=$KS/private/sperrliste; mkdir -p "$DB"
[ -f "$DB/index.txt" ] || { touch "$DB/index.txt"; echo 1000 > "$DB/crlnumber"; }
cat > "$DB/ca.cnf" <<CNF
[ca]
default_ca = haus
[haus]
database = $DB/index.txt
crlnumber = $DB/crlnumber
default_md = sha256
default_crl_days = 30
CNF
CA="-config $DB/ca.cnf -cert $KS/public/identity_ca.cert.pem"
CA="$CA -keyfile $KS/private/identity_ca.key.pem"
openssl ca $CA -revoke "$KS/enclaves$ENCLAVE/cert.pem"
openssl ca $CA -gencrl -out "$KS/public/crl.pem"
# Jede Enclave prüft ihre Gegenüber mit dieser Liste (Datei crl.pem im Enclave-Ordner)
find "$KS/enclaves" -name cert.pem -execdir cp "$KS/public/crl.pem" crl.pem \;
openssl crl -in "$KS/public/crl.pem" -noout -text | grep -A1 "Serial Number"
