#!/bin/bash
# Daily Bug Bounty Automation
# - Runs scheduled scans
# - Updates daily log
# - Generates reports
# - Sends reminders

set -euo pipefail

BASE_DIR="/home/wasim/bug-bounty"
SCRIPTS_DIR="$BASE_DIR/automation"
LOGS_DIR="$BASE_DIR/logs"
DAILY_DIR="$BASE_DIR/daily-logs"
REPORTS_DIR="$BASE_DIR/reports"
PROGRAMS_DIR="$BASE_DIR/programs"

DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOGS_DIR/daily_run_$TIMESTAMP.log"

echo "=== Bug Bounty Daily Automation — $DATE ===" | tee "$LOG_FILE"

# 1. Run parameter discovery on today's targets
echo "[$(date)] Running parameter discovery..." | tee -a "$LOG_FILE"
if [ -f "$SCRIPTS_DIR/targets.txt" ]; then
    while read -r url; do
        echo "  Scanning: $url" | tee -a "$LOG_FILE"
        python3 "$SCRIPTS_DIR/scan_runner.py" "$url" --mode xss redirect --output "$REPORTS_DIR/scan_$TIMESTAMP.jsonl" 2>&1 | tee -a "$LOG_FILE"
        sleep 2
    done < "$SCRIPTS_DIR/targets.txt"
else
    echo "  No targets file found at $SCRIPTS_DIR/targets.txt" | tee -a "$LOG_FILE"
fi

# 2. Generate daily report
echo "[$(date)] Generating daily report..." | tee -a "$LOG_FILE"
python3 "$SCRIPTS_DIR/daily_tracker.py" report 2>&1 | tee -a "$LOG_FILE" || true

# 3. Show weekly summary
echo "[$(date)] Weekly summary:" | tee -a "$LOG_FILE"
python3 "$SCRIPTS_DIR/daily_tracker.py" week 2>&1 | tee -a "$LOG_FILE" || true

# 4. Git commit if in a git repo
if [ -d "$BASE_DIR/.git" ]; then
    cd "$BASE_DIR"
    git add -A 2>/dev/null || true
    git commit -m "bugbounty: daily run $DATE" --no-verify 2>/dev/null || true
fi

echo "=== Automation complete ===" | tee -a "$LOG_FILE"
