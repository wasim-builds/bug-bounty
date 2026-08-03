#!/bin/bash
# Daily Bug Bounty Workflow — 3 Step Routine
# Usage: bash daily_start.sh

echo "========================================"
echo "🐛 Daily Bug Bounty Workflow"
echo "========================================"

STEP1_DONE=false
STEP2_DONE=false
STEP3_DONE=false

# Step 1: Check status
echo ""
echo "📊 STEP 1: Check yesterday's activity"
echo "----------------------------------------"
python3 /home/wasim/bug-bounty/automation/daily_tracker.py today
python3 /home/wasim/bug-bounty/automation/daily_tracker.py week
echo ""
read -p "Step 1 done? Press Enter to continue..."

# Step 2: Recon a target
echo ""
echo "🔍 STEP 2: Recon a target"
echo "----------------------------------------"
read -p "Enter target domain (e.g., target.com): " target
if [ -n "$target" ]; then
    python3 /home/wasim/bug-bounty/recon/scripts/recon_runner.py "$target" --skip-nuclei
    STEP2_DONE=true
else
    echo "Skipping recon."
fi

# Step 3: Scan for bugs
echo ""
echo "🛠️  STEP 3: Scan for bugs"
echo "----------------------------------------"
if [ "$STEP2_DONE" = true ]; then
    echo "Available URLs from recon:"
    ls -1 /home/wasim/bug-bounty/recon/output/*/urls.txt 2>/dev/null | head -5
    echo ""
fi
read -p "Enter URL to scan (with query params) or press Enter to skip: " scan_url
if [ -n "$scan_url" ]; then
    python3 /home/wasim/bug-bounty/automation/master_scanner.py "$scan_url" \
        --modes xss redirect csrf ssrf auth sqli \
        --output-dir /home/wasim/bug-bounty/reports
    STEP3_DONE=true
else
    echo "Skipping scan."
fi

# Summary
echo ""
echo "========================================"
echo "✅ Daily workflow complete!"
echo "========================================"
echo ""
echo "What you did:"
echo "  Step 1 (Status): ✅"
echo "  Step 2 (Recon):  $([ "$STEP2_DONE" = true ] && echo '✅' || echo '⏭️  skipped')"
echo "  Step 3 (Scan):   $([ "$STEP3_DONE" = true ] && echo '✅' || echo '⏭️  skipped')"
echo ""
echo "Next steps:"
echo "  1. Review reports/ for hits"
echo "  2. Log results: python3 automation/daily_tracker.py add ..."
echo "  3. Submit valid findings to HackerOne"
echo ""
