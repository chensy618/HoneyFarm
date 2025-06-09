#!/bin/bash

# Usage: ./run.sh <room> <status>

ROOM=$1
STATUS=$2
LOGFILE="/opt/lighting-control/lighting.log"

if [[ -z "$ROOM" || -z "$STATUS" ]]; then
  echo "Usage: $0 <room> <status>"
  exit 1
fi

echo "$(date) - Room: $ROOM | State: $STATUS" >> "$LOGFILE"

echo "[INFO] Light status updated: Room '$ROOM' set to '$STATUS'."
