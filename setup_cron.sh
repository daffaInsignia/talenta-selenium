#!/usr/bin/env bash
# Setup crontab for Talenta Auto Attendance (Linux)
# Usage: chmod +x setup_cron.sh && ./setup_cron.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_SCRIPT="$SCRIPT_DIR/run.sh"

chmod +x "$RUN_SCRIPT"

# Remove existing talenta cron entries
crontab -l 2>/dev/null | grep -v "talenta-auto-login" > /tmp/cron_clean

# Every 5 minutes, check and clock in/out if needed
cat >> /tmp/cron_clean <<EOF
# Talenta Auto Attendance - check every 5 minutes
*/5 * * * * $RUN_SCRIPT # talenta-auto-login
EOF

crontab /tmp/cron_clean
rm /tmp/cron_clean

echo "============================================"
echo " Talenta Auto Attendance - Cron Setup"
echo "============================================"
echo ""
echo "Installed cron jobs:"
crontab -l | grep "talenta-auto-login"
echo ""
echo "Logs: $SCRIPT_DIR/cron.log"
echo ""
echo "To remove: crontab -e (delete talenta lines)"
echo "To check:  crontab -l | grep talenta"
echo "============================================"
