#!/bin/bash

echo "[RECEIVE] Listening for report metadata..."

REPORT_NAME=${1:-"report_$(date +%s).txt"}

NODE_NAME=$(echo "$REPORT_NAME" | cut -d'_' -f1)

MONTH_ID=$(date +%Y-%m)

LOG_DIR="/diagnostics/$NODE_NAME"
LOG_FILE="$LOG_DIR/report-$MONTH_ID.log"

mkdir -p "$LOG_DIR"

echo "[LOG] $REPORT_NAME received at $(date)" >> "$LOG_FILE"

echo "[RECEIVE] Log entry written to $LOG_FILE"
