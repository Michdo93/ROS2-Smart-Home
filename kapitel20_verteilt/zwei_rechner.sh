#!/usr/bin/env bash
# Kapitel 20: zwei Rechner auf einem simulieren – "pi" (10.7.0.2) und
# "server" (10.7.0.3) in Netzwerk-Namensräumen, verbunden über br7 (10.7.0.1).
#   sudo ./zwei_rechner.sh an          # einrichten
#   sudo ip netns exec pi bash         # Terminal "auf dem Pi"
#   sudo ./zwei_rechner.sh aus         # entfernen (vorher Programme darin beenden)
set -euo pipefail
case ${1:?an oder aus} in
an)
  ip link add br7 type bridge
  ip link set br7 up
  ip addr add 10.7.0.1/24 dev br7
  nr=2
  for name in pi server; do
    ip netns add "$name"
    ip link add "v-$name" type veth peer name eth0 netns "$name"
    ip link set "v-$name" master br7 up
    ip netns exec "$name" ip addr add "10.7.0.$nr/24" dev eth0
    ip netns exec "$name" ip link set eth0 up
    ip netns exec "$name" ip link set lo up
    ip netns exec "$name" ip route add default via 10.7.0.1
    nr=$((nr + 1))
  done ;;
aus)
  for name in pi server; do ip netns del "$name" 2>/dev/null || true; done
  ip link del br7 2>/dev/null || true ;;
esac
