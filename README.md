# Bug Bounty Hunting Workspace

Automated daily hunting tracker + custom scanners + program scope reference.

## Structure

```
bug-bounty/
├── automation/
│   ├── daily_runner.sh       # Cron job entrypoint
│   ├── daily_tracker.py      # Add/view daily entries
│   └── scan_runner.py        # Wrapper for scanners
├── scanners/
│   ├── xss_redirect_scanner.py  # XSS + open redirect scanner
│   ├── csrf_scanner.py          # CSRF token missing detector
│   ├── ssrf_scanner.py          # SSRF payload tester
│   ├── auth_bypass_scanner.py   # Auth bypass + IDOR checker
│   └── sqli_scanner.py          # SQL injection error-based detector
├── programs/
│   ├── google/scope.md
│   ├── microsoft/scope.md
│   ├── github/scope.md
│   ├── shopify/scope.md
│   └── slack/scope.md
├── daily-logs/               # JSONL hunting logs by date
├── reports/                  # Daily Markdown reports
├── logs/                     # Automation logs
└── README.md
```

## Daily Workflow

### 1. Start Hunting
```bash
cd /home/wasim/bug-bounty

# Log a new target
python3 automation/daily_tracker.py add \
  --program google \
  --target "https://www.google.com/search?q=test" \
  --type xss \
  --status testing \
  --notes "Testing search param for reflected XSS" \
  --time 30
```

### 2. Run Scans
```bash
# Scan a single target for XSS + redirect
python3 scanners/xss_redirect_scanner.py "https://target.com/search?q=test" \
  --mode xss redirect \
  --output reports/scan_results.jsonl

# Scan for CSRF
python3 scanners/csrf_scanner.py "https://target.com/page" \
  --output reports/csrf_scan.jsonl

# Scan for SSRF
python3 scanners/ssrf_scanner.py "https://target.com/proxy?url=https://evil.com" \
  --output reports/ssrf_scan.jsonl

# Scan for auth bypass + IDOR
python3 scanners/auth_bypass_scanner.py "https://target.com/profile?id=1" \
  --output reports/auth_scan.jsonl

# Scan for SQLi
python3 scanners/sqli_scanner.py "https://target.com/search?q=test" \
  --output reports/sqli_scan.jsonl

# Run ALL scanners on a target
python3 automation/master_scanner.py "https://target.com/search?q=test&url=https://evil.com" \
  --modes xss redirect csrf ssrf auth sqli \
  --output-dir reports

# Run daily automation (targets from automation/targets.txt)
bash automation/daily_runner.sh
```

### 3. Review & Report
```bash
# View today's entries
python3 automation/daily_tracker.py today

# View weekly summary
python3 automation/daily_tracker.py week

# Generate daily report
python3 automation/daily_tracker.py report
# Output: reports/report_YYYY-MM-DD.md
```

### 4. Submit Findings
```bash
# Log a submission
python3 automation/daily_tracker.py add \
  --program github \
  --target "https://github.com/search?q=test" \
  --type xss \
  --status submitted \
  --notes "Reported via HackerOne #12345" \
  --time 120
```

## Cron Automation

Daily at 9:00 AM:
- Runs scans on `automation/targets.txt`
- Generates daily report
- Commits results to git

Edit targets: `nano /home/wasim/bug-bounty/automation/targets.txt`

## Scanners

| Scanner | Bug Class | Usage |
|---------|-----------|-------|
| `scanners/xss_redirect_scanner.py` | XSS + Open Redirect | `python3 scanners/xss_redirect_scanner.py "https://target.com/search?q=test" --mode xss redirect` |
| `scanners/csrf_scanner.py` | CSRF | `python3 scanners/csrf_scanner.py "https://target.com/page" "https://target.com/form"` |
| `scanners/ssrf_scanner.py` | SSRF | `python3 scanners/ssrf_scanner.py "https://target.com/proxy?url=https://evil.com"` |
| `scanners/auth_bypass_scanner.py` | Auth Bypass + IDOR | `python3 scanners/auth_bypass_scanner.py "https://target.com/profile?id=1"` |
| `scanners/sqli_scanner.py` | SQL Injection | `python3 scanners/sqli_scanner.py "https://target.com/search?q=test"` |

### Master Runner
Run multiple scanners at once:
```bash
python3 automation/master_scanner.py "https://target.com/search?q=test&redirect=https://evil.com" \
  --modes xss redirect csrf ssrf auth sqli \
  --output-dir reports
```

## Programs Reference

| Program | Scope | Quick Win | Payout |
|---------|-------|-----------|--------|
| Google | `programs/google/scope.md` | XSS on search params | $100-$15K |
| Microsoft | `programs/microsoft/scope.md` | Azure auth bypass | $200-$250K |
| GitHub | `programs/github/scope.md` | Actions injection | $500-$25K |
| Shopify | `programs/shopify/scope.md` | Store redirect | $500-$10K |
| Slack | `programs/slack/scope.md` | OAuth flows | $500-$5K |

## Tracker Commands

```bash
# Add entry
python3 automation/daily_tracker.py add --program <program> --target <url> --type <bug_type> --status <status> --time <minutes>

# View
python3 automation/daily_tracker.py today
python3 automation/daily_tracker.py week
python3 automation/daily_tracker.py report

# Bug types: xss, redirect, csrf, ssrf, sqli, rce, lfi, auth, info, other
# Status: testing, needs-poc, submitted, duplicate, not-a-bug, accepted, paid, closed
```

## Tips

1. **Focus on one program at a time** — learn their tech stack
2. **Automate recon** — use the daily runner for parameter discovery
3. **Log everything** — even failed attempts, they show consistency
4. **Quality over quantity** — 1 good report > 10 duplicates
