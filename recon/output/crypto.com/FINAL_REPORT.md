# Crypto.com Bug Bounty Recon Report
**Date:** 2026-08-03  
**Program:** https://hackerone.com/crypto  
**Bounty:** $1 - $1,000,000  
**Researcher:** wasim-builds  

---

## Executive Summary

Performed reconnaissance on crypto.com attack surface. Found **1,120 subdomains**, **263 alive hosts**, and identified **high-value targets** for manual verification. Automated scanning was limited by Cloudflare WAF and network timeouts. **No confirmed vulnerabilities** — findings require manual browser-based verification.

---

## Recon Results

### Subdomain Enumeration
- **Tool:** subfinder
- **Subdomains found:** 1,120
- **Source:** passive DNS, certificate transparency, search engines

### Alive Hosts
- **Tool:** httpx
- **Alive hosts:** 263
- **Technologies detected:** Cloudflare, Amazon CloudFront, Kong, Express, Nginx, Azure Front Door, Next.js, React

---

## High-Value Targets

### Authentication & Account Flows
| Subdomain | Status | Tech | Notes |
|-----------|--------|------|-------|
| `auth.crypto.com` | 301 | Cloudflare | Redirect chain — test for open redirect |
| `accounts.crypto.com` | 200 | Unknown | Account pages — test for IDOR/auth bypass |
| `auth.custody.crypto.com` | 302 | HSTS, Nginx | Custody auth — redirect params |
| `auth.travel.crypto.com` | 200 | Amazon ALB, CloudFront | Travel auth flow |
| `authws.crypto.com` | 200 | Unknown | Auth websocket endpoint |

### API Endpoints
| Subdomain | Status | Tech | Notes |
|-----------|--------|------|-------|
| `api.nft.crypto.com` | 200 | Cloudflare, Express, Kong | NFT API — test for SSRF/injection |
| `api.crypto.com` | 404 | Cloudflare, Kong | API gateway — check for info disclosure |
| `api.crypto-coin-info-api.crypto.com` | 200 | Cloudflare | Coin info API |
| `api-internal.titan.crypto.com` | 403 | Cloudflare | Internal API — potential info leak in 403 |
| `risk-core-api.crypto.com` | 403 | Cloudflare | Risk API — check error messages |

### Web Applications
| Subdomain | Status | Tech | Notes |
|-----------|--------|------|-------|
| `blinks.crypto.com` | 307 | Cloudflare, Next.js, React | DeFi Wallet swap — XSS/redirect targets |
| `wallet.crypto.com` | 200 | Cloudflare | Wallet app — auth/session bugs |
| `help.crypto.com` | 302 | Cloudflare | Help center — XSS in search/params |
| `chat.crypto.com` | 200 | CloudFront, reCAPTCHA | Chat app — SSRF/auth issues |
| `experiences.crypto.com` | 200 | CloudFront, Next.js | Travel/events — booking logic flaws |
| `tickets.crypto.com` | 200 | CloudFront, Next.js | Event tickets — price/IDOR bugs |
| `status.crypto.com` | 200 | Atlassian Statuspage | Third-party — check for subdomain takeover |
| `merchant.crypto.com` | 200 | Cloudflare, GeeTest | Merchant dashboard — business logic |

### Internal/Interesting
| Subdomain | Status | Notes |
|-----------|--------|-------|
| `internal.titan.crypto.com` | 403 | Internal system — check for info disclosure |
| `internal-webview.titan.crypto.com` | 403 | Webview endpoints |
| `internal-api-warmup.titan.crypto.com` | 403 | API warmup — potential misconfig |
| `grafana.crypto-nft-bridge-api.crypto.com` | 403 | Grafana dashboard — potential exposure |
| `jenkins.crypto-coin-info-api.crypto.com` | 404 | CI/CD — check for subdomain takeover |
| `gitlab.coin-price-sse-auth.crypto.com` | 200 | GitLab instance — check for auth issues |
| `dprd.crypto.com` | 403 | Pre-production environment |
| `black-cat.crypto.com` | 400 | Internal service — check for info leak |

---

## Crawled URLs

- **URLs discovered:** 43
- **Parameters found:** 0 from automated crawl
- **Note:** Most crypto.com apps are SPAs or heavily JavaScript-based. Traditional crawlers may miss dynamic routes.

### Sample URLs Found
- `https://auth.custody.crypto.com`
- `https://custody.crypto.com`
- `https://crypto-sentiment-api.crypto.com`
- `https://ai-agent-api.crypto.com`
- `http://wallet-asset-dashboard-api.crypto.com`

---

## Potential Bug Classes

### 1. Open Redirect (HIGH PRIORITY)
**Why:** Multiple 301/302/307 redirect endpoints  
**Targets:**
- `auth.crypto.com` (301)
- `accounts.crypto.com` (200 — check for redirect params)
- `auth.custody.crypto.com` (302)
- `document-hub.crypto.com` (307)
- `help.crypto.com` (302)
- `pay.crypto.com` (302)

**Test:**
```bash
# Common redirect parameters
redirect
redirect_uri
return_url
next
url
continue
callback
target
dest
destination

# Example test URLs
https://auth.crypto.com?redirect=https://evil.com
https://accounts.crypto.com?return_url=https://evil.com
https://help.crypto.com?next=https://evil.com
```

**Impact:** Phishing, OAuth bypass, SSRF via redirect

---

### 2. SSRF (MEDIUM PRIORITY)
**Why:** API endpoints that may fetch external resources  
**Targets:**
- `api.nft.crypto.com` (Express/Kong)
- `ai-agent-api.crypto.com` (503 — AI agent may fetch URLs)
- `risk-core-api.crypto.com` (403)
- `price-external-api.crypto.com` (403)

**Test:** Look for parameters like `url`, `uri`, `link`, `image`, `avatar`, `webhook`, `callback`

---

### 3. XSS (MEDIUM PRIORITY)
**Why:** Search/input fields in web apps  
**Targets:**
- `blinks.crypto.com` (Next.js — DeFi swap)
- `help.crypto.com` (help center search)
- `chat.crypto.com` (chat app)
- `experiences.crypto.com` (travel booking)

**Test:** Search params, input fields, URL fragments

---

### 4. Auth Bypass / IDOR (MEDIUM PRIORITY)
**Why:** Account and wallet endpoints  
**Targets:**
- `accounts.crypto.com`
- `wallet.crypto.com`
- `wallet-nft.crypto.com`
- `wallet-analysis.crypto.com`

**Test:** Change IDs in URLs, test token handling, check for broken access control

---

### 5. Information Disclosure (LOW-MEDIUM)
**Why:** Error pages, debug endpoints, internal services  
**Targets:**
- `internal.titan.crypto.com` (403 — check error body)
- `grafana.crypto-nft-bridge-api.crypto.com` (403)
- `jenkins.crypto-coin-info-api.crypto.com` (404)
- `api.crypto.com` (404 — check for stack traces)

---

### 6. Subdomain Takeover (LOW PRIORITY)
**Why:** Some endpoints return 404 but may have unclaimed DNS  
**Targets:**
- `jenkins.crypto-coin-info-api.crypto.com`
- `status.crypto.com` (Atlassian Statuspage — check CNAME)
- Various `*.dprd.crypto.com` subdomains

---

## Manual Testing Checklist

### Phase 1: Open Redirect Testing
```bash
# 1. Check auth.crypto.com redirect chain
curl -I "https://auth.crypto.com"

# 2. Test common redirect parameters
curl -I "https://auth.crypto.com?redirect=https://evil.com"
curl -I "https://accounts.crypto.com?return_url=https://evil.com"
curl -I "https://help.crypto.com?next=https://evil.com"

# 3. Check if redirects are validated
# Look for: 302 to evil.com = vulnerable
# Look for: 302 to internal page = maybe safe
# Look for: 200 = not a redirect
```

### Phase 2: OAuth/OAuth2 Testing
```bash
# Check oauth2.crypto.com
curl -I "https://oauth2.crypto.com"
curl -I "https://wallet-oauth2.crypto.com"

# Look for authorization endpoints
# Test redirect_uri validation
```

### Phase 3: API Testing
```bash
# Check API responses for info disclosure
curl "https://api.crypto.com" -H "Accept: application/json"
curl "https://api.nft.crypto.com" -H "Accept: application/json"

# Test for SSRF on AI agent API
curl "https://ai-agent-api.crypto.com/fetch?url=https://evil.com"
```

### Phase 4: Browser-Based Testing
1. Open browser with dev tools
2. Navigate to `https://auth.crypto.com`
3. Follow redirect chain
4. Look for redirect parameters in URL
5. Test payloads manually
6. Check for reflected XSS in responses

---

## Scan Results

### Automated Scanner Output
- **XSS scanner:** Ran on `https://www.google.com/search?q=test` — 1 false positive
- **Master scanner:** Timeout on crypto.com targets due to network restrictions
- **Nuclei:** Skipped due to template database not available

### Why Automated Scans Failed
1. **Cloudflare WAF** — blocks automated requests
2. **Network timeouts** — some endpoints are slow/unreachable from our IP
3. **JavaScript-heavy apps** — traditional crawlers can't discover dynamic routes
4. **No query parameters** in crawled URLs — SPAs use path-based routing

---

## Recommendations

### Immediate Actions
1. **Test open redirects manually** — highest probability, highest impact
2. **Check auth flows in browser** — use dev tools to inspect requests
3. **Look for OAuth misconfigurations** — common in crypto/fintech
4. **Test wallet/account endpoints** — IDOR/auth bypass

### Tools to Use
```bash
# Browser extensions
- HackTools
- FoxyProxy
- Wappalyzer

# Manual testing
- Burp Suite Community
- Browser dev tools
- curl for quick checks

# Parameter discovery
- Arjun
- Param Miner
- URL fuzzing with ffuf
```

### Report Quality Tips
1. **Include PoC video** — screen recording of the bug
2. **Show impact clearly** — user funds, data, accounts at risk
3. **Check Hacktivity first** — avoid duplicates
4. **Be specific** — exact URL, parameter, payload, steps
5. **Suggest fix** — show you understand the issue

---

## Program Rules Reminders

From Crypto.com HackerOne page:
- ✅ Open scope — all crypto.com owned assets
- ✅ Gold Standard Safe Harbor
- ✅ 100% response rate
- ✅ Payment within 1 month
- ❌ No user/personnel targeting
- ❌ No social engineering
- ❌ No malware/deceptive software
- ❌ No unauthorized data collection

**Smart contracts in scope:**
- `0x2e53c5586e12a99d4CAE366E9Fc5C14fE9c6495d` — Cronos explorer
- `0xfe18ae03741a5b84e39c295ac9c856ed7991c38e` — CDCETH

---

## Next Steps

1. **Manual browser testing** on `auth.crypto.com` redirects
2. **Check Hacktivity** for recent crypto.com reports
3. **Test OAuth flows** if accessible
4. **Draft report** if you find something legitimate
5. **Submit via HackerOne** with clear PoC

---

## Files Generated
- `recon/output/crypto.com/subfinder.txt` — 1,120 subdomains
- `recon/output/crypto.com/alive.txt` — 263 alive hosts
- `recon/output/crypto.com/urls.txt` — 43 crawled URLs
- `recon/output/crypto.com/parameters.txt` — 0 params from automated crawl
- `recon/output/crypto.com/recon_report.md` — this report

---

**Status:** Recon complete. No confirmed vulnerabilities. Manual verification required.
