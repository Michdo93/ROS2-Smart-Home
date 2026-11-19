#!/usr/bin/env bash
# Kapitel 11: Speicher und Rechenzeit eines laufenden Knotens (Name des Programms als Argument)
#   ./ressourcen.sh openhab_bridge
PID=$(pgrep -n -f "lib/.*/$1( |$)") || { echo "$1 läuft nicht"; exit 1; }
ps -o rss=,etimes=,times= -p "$PID" | awk '{printf "Speicher %.1f MB, Laufzeit %d s, CPU-Zeit %d s\n", $1/1024, $2, $3}'
