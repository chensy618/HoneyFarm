#!/bin/bash

# Thermostat Control Script
# Usage: ./run.sh <room> <delta>

ROOM=$1
DELTA=$2
LOGFILE="/opt/thermostat-control/thermostat.log"

if [[ -z "$ROOM" || -z "$DELTA" ]]; then
  echo "Usage: $0 <room> <delta>"
  exit 1
fi

echo "$(date) - Room: $ROOM | Temperature change: $DELTA C" >> "$LOGFILE"

echo "[INFO] Thermostat updated: Room '$ROOM' temperature adjusted by $DELTA C."
