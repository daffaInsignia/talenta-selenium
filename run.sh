#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
source venv/bin/activate
export HEADLESS=true
python scheduler.py --once >> "$SCRIPT_DIR/cron.log" 2>&1
