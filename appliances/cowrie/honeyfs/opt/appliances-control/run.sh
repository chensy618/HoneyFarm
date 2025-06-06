#!/bin/bash

LOGFILE="/opt/appliances-control/appliance.log"
STATUSFILE="/opt/appliances-control/status.json"

echo "[INFO] Dashboard command received: $1 at $(date)" >> "$LOGFILE"

case "$1" in
  refrigerator)
    echo "[INFO] Setting Refrigerator to 4°C" >> "$LOGFILE"
    cat <<EOF > "$STATUSFILE"
{
  "device": "refrigerator",
  "state": "on",
  "target_temperature": 4,
  "last_updated": "$(date -Iseconds)"
}
EOF
    ;;

  coffeemaker)
    echo "[INFO] Coffee Maker strength set to 3, powered ON" >> "$LOGFILE"
    cat <<EOF > "$STATUSFILE"
{
  "device": "coffee_maker",
  "state": "on",
  "strength": 3,
  "last_updated": "$(date -Iseconds)"
}
EOF
    ;;

  washer)
    echo "[INFO] Washing Machine started (mode: quick)" >> "$LOGFILE"
    cat <<EOF > "$STATUSFILE"
{
  "device": "washing_machine",
  "state": "running",
  "mode": "quick",
  "last_updated": "$(date -Iseconds)"
}
EOF
    ;;

  *)
    echo "[WARN] Unknown appliance: $1" >> "$LOGFILE"
    ;;
esac
