# Crypto.com Bug Bounty Recon Report
Generated: 2026-08-02

## Summary
- **Program:** Crypto.com (HackerOne)
- **Bounty:** $1 - $1,000,000
- **Response efficiency:** 100%
- **Total paid:** $1,618,875
- **90-day reports:** 1022
- **Average bounty:** $484 - $600

## Recon Results

### Subdomains Found
- Total subdomains: 560 (subfinder) + amass results pending
- Alive hosts: 261

### High-Value Targets

| Subdomain | Status | Tech | Notes |
|-----------|--------|------|-------|
| auth.crypto.com | 301 | Cloudflare | Likely redirects to login |
| accounts.crypto.com | 307 | Cloudflare | Account-related, potential redirect |
| auth.custody.crypto.com | 302 | HSTS, Nginx | Custody auth flow |
| api.nft.crypto.com | 200 | Cloudflare, Express, Kong | NFT API |
| api.crypto.com | 404 | Cloudflare, Kong | API gateway |
| blinks.crypto.com | 307 | Cloudflare, Next.js, React | DeFi Wallet swap |
| authws.crypto.com | 502 | Cloudflare | Auth websocket? |
| ai-agent-api.crypto.com | 200 | Unknown | AI agent API |

### Potential Bug Classes to Test

1. **Open Redirect** — auth.crypto.com, accounts.crypto.com redirect with 307/301
2. **SSRF** — API endpoints that fetch external URLs
3. **XSS** — Search/query params in web apps
4. **Auth Bypass** — Token handling in auth flows
5. **Information Disclosure** — Error messages, debug endpoints
6. **Business Logic** — Crypto transaction flows, wallet operations

## Recommended Next Steps

### Phase 1: Manual Recon
```bash
# 1. Check redirect chains
curl -I https://auth.crypto.com
curl -I https://accounts.crypto.com

# 2. Look for redirect parameters
# Common params: redirect_uri, return_url, next, url, continue

# 3. Test OAuth flows if present
# Look for: /oauth/authorize, /login, /signin
```

### Phase 2: Parameter Discovery
```bash
# Run Arjun/Param Miner on auth/account pages
# Look for hidden parameters

# Extract from JS files
katana -list crawl_targets.txt -depth 3 -o urls.txt
cat urls.txt | unfurl keys > parameters.txt
```

### Phase 3: Active Testing
```bash
# Test open redirects
python3 scanners/xss_redirect_scanner.py "https://auth.crypto.com?redirect=https://evil.com" \
  --mode redirect

# Test auth bypass
python3 scanners/auth_bypass_scanner.py "https://accounts.crypto.com/profile?id=1"

# Test SSRF on API endpoints
python3 scanners/ssrf_scanner.py "https://api.crypto.com/proxy?url=https://evil.com"
```

### Phase 4: Manual Verification
- Check every finding in a real browser
- Verify impact on user data/funds
- Document steps clearly
- Draft report with PoC

## Important Reminders
- Stay strictly in scope: crypto.com owned assets only
- Do NOT target users or employees
- Do NOT exfiltrate real user data
- Stop at proof-of-concept
- Submit only legitimate findings

## Report Template
```
Title: [Type] Short description of vulnerability

Summary: 1-2 sentences

Steps to Reproduce:
1. Go to https://target.com/?param=value
2. Inject payload: <payload>
3. Observe: <result>

Impact: What can an attacker do?

Remediation: Suggested fix
```
