# Crypto.com Bug Bounty — Quick Start Guide

## Program Info
- **URL:** https://hackerone.com/crypto
- **Bounty:** $1 - $1,000,000
- **Triage:** 100% response, ~16 hours first response
- **Scope:** Open — all crypto.com owned assets
- **Total Paid:** $1,618,875

## Run Recon Locally

```bash
cd /home/wasim/bug-bounty

# Option 1: Run the automated script
bash recon/scripts/crypto_recon.sh

# Option 2: Manual step-by-step
subfinder -d crypto.com -o recon/output/crypto.com/subfinder.txt -silent
cat recon/output/crypto.com/subfinder.txt | httpx -silent -status-code -title -tech-detect -o recon/output/crypto.com/alive.txt
```

## What to Look For

### 1. Open Redirect (High Probability)
**Targets:** `auth.crypto.com`, `accounts.crypto.com`
**Test:**
```bash
# Check if these redirect
curl -I "https://auth.crypto.com?redirect=https://evil.com"
curl -I "https://accounts.crypto.com?return_url=https://evil.com"

# Common params to test:
# redirect, redirect_uri, return_url, next, url, continue, callback
```

### 2. SSRF (Medium Probability)
**Targets:** API endpoints, NFT API, price APIs
**Test:**
```bash
# Look for proxy/fetch parameters
python3 scanners/ssrf_scanner.py "https://api.crypto.com/proxy?url=https://evil.com"
python3 scanners/ssrf_scanner.py "https://api.nft.crypto.com/fetch?url=https://evil.com"
```

### 3. XSS (Low-Medium Probability)
**Targets:** Search pages, help centers, blinks.crypto.com
**Test:**
```bash
python3 scanners/xss_redirect_scanner.py "https://blinks.crypto.com/search?q=test" \
  --mode xss
```

### 4. Auth Bypass / IDOR (Medium Probability)
**Targets:** accounts.crypto.com, auth endpoints
**Test:**
```bash
# Test if changing IDs in URLs works
python3 scanners/auth_bypass_scanner.py "https://accounts.crypto.com/profile?id=1"
```

## Manual Testing Checklist

### Before Scanning:
1. Read scope page completely: https://hackerone.com/crypto
2. Note excluded assets (user targeting, social engineering)
3. Set up a test account if needed (KYC may be required for app)
4. Use browser dev tools to inspect requests

### During Testing:
1. Test redirects first — easiest to find, high impact
2. Look for OAuth flows — common redirect_uri issues
3. Check API endpoints for SSRF
4. Test for XSS in search/input fields
5. Look for information disclosure in error messages

### Before Reporting:
1. Verify the bug is reproducible
2. Check it's not already reported (search Hacktivity)
3. Assess real impact (user funds, data, accounts)
4. Prepare clear steps to reproduce
5. Include PoC/screenshots/video

## Report Template

```
Title: Open Redirect on auth.crypto.com via redirect_uri parameter

Summary: auth.crypto.com redirects to attacker-controlled domains via unvalidated redirect_uri parameter, enabling phishing attacks.

Steps to Reproduce:
1. Visit https://auth.crypto.com?redirect_uri=https://evil.com
2. Observe HTTP 302 redirect to https://evil.com
3. User credentials can be phished via attacker-controlled domain

Impact: 
- Phishing attacks against Crypto.com users
- Credential theft via fake login pages
- Bypasses same-origin policy protections

Remediation:
- Validate redirect_uri against whitelist
- Use relative paths for internal redirects
- Implement strict origin checks

References:
- OWASP Open Redirect: https://owasp.org/www-community/attacks/Open_redirect
```

## Commands Cheat Sheet

```bash
# Daily status
bounty-start

# Run full recon on crypto.com
bash recon/scripts/crypto_recon.sh

# Manual scan on a specific URL
python3 automation/master_scanner.py "https://target.com?param=value" \
  --modes xss redirect ssrf auth \
  --output-dir reports

# Log finding in tracker
python3 automation/daily_tracker.py add \
  --program crypto \
  --target "https://auth.crypto.com" \
  --type redirect \
  --status testing \
  --time 30
```

## Important Notes

1. **Crypto.com uses Cloudflare WAF** — some scans may be blocked
2. **KYC required for app access** — web targets are your best entry point
3. **Open scope means everything** — focus on high-impact assets first
4. **100% triage rate** — every report gets reviewed, quality matters
5. **Do NOT test on real users** — stay in scope, no social engineering

## Your Advantage
- 5 HackerOne signal points = full submission access
- Open-source background = understanding of secure coding
- Automated recon tools = faster discovery
- Consistent tracking = better hunting rhythm

## Next Action
Run `bash recon/scripts/crypto_recon.sh` and share the output. I'll help you interpret results and identify the most promising targets.
