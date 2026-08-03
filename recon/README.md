# Bug Bounty Recon Toolkit

Fast, automated reconnaissance pipeline for bug bounty hunting.

## Installed Tools

| Tool | Purpose | Version |
|------|---------|---------|
| `subfinder` | Subdomain enumeration (passive) | v2.14.0 |
| `amass` | Deep subdomain + ASN recon | v4.2.0 |
| `httpx` | HTTP probing + tech detection | v1.9.0 |
| `katana` | Web crawler | v1.0.0 |
| `waybackurls` | Historical URLs from Wayback | v0.1.0 |
| `gau` | URLs from Common Crawl + Wayback | v2.x |
| `unfurl` | Parameter extraction from URLs | latest |
| `ffuf` | Web fuzzer | v2.x |
| `naabu` | Fast port scanner | latest |

## Quick Start

```bash
# Full recon on a target
python3 /home/wasim/bug-bounty/recon/scripts/recon_runner.py example.com

# Output goes to: /home/wasim/bug-bounty/recon/output/example.com/
```

## What It Does

1. **Subdomain Enumeration** — `subfinder` + `amass`
2. **HTTP Probing** — `httpx` (status, title, tech stack)
3. **Port Scanning** — `naabu` (top 100 ports)
4. **Web Crawling** — `katana` (depth 3)
5. **Historical URLs** — `waybackurls` + `gau`
6. **Parameter Extraction** — `unfurl`
7. **Vulnerability Scanning** — `nuclei` (if installed)

## Output Structure

```
recon/output/example.com/
├── subdomains.txt      # All discovered subdomains
├── subfinder.txt       # From subfinder
├── amass.txt           # From amass
├── alive.txt           # HTTP alive hosts (with status/title/tech)
├── httpx_raw.txt       # Raw httpx output
├── urls.txt            # Crawled URLs from katana
├── historical_urls.txt # Wayback + Common Crawl URLs
├── wayback.txt         # Wayback URLs
├── gau.txt             # gau URLs
├── parameters.txt      # Unique query parameters
├── ports.txt           # Open ports
├── nuclei_results.txt  # Nuclei findings (if run)
└── summary.txt         # Quick stats
```

## Usage Examples

```bash
# Full recon pipeline
python3 recon/scripts/recon_runner.py target.com

# Subdomains only
python3 recon/scripts/recon_runner.py target.com --subdomains-only

# URLs only (skip subdomain enum)
python3 recon/scripts/recon_runner.py target.com --urls-only

# Skip nuclei (faster)
python3 recon/scripts/recon_runner.py target.com --skip-nuclei

# Custom output directory
python3 recon/scripts/recon_runner.py target.com --output /tmp/recon
```

## Manual Tool Usage

```bash
# Subdomain enumeration
subfinder -d target.com -o subdomains.txt
amass enum -d target.com -o amass.txt

# Probe for alive hosts
cat subdomains.txt | httpx -status-code -title -tech-detect

# Crawl for URLs
katana -list alive.txt -depth 3 -silent

# Historical URLs
waybackurls target.com > wayback.txt
gau target.com > gau.txt

# Extract parameters
cat urls.txt | unfurl keys > parameters.txt

# Port scan
naabu -host target.com -top-ports 100

# Fuzz endpoints
ffuf -u https://target.com/FUZZ -w wordlist.txt
```

## Integration with Bug Bounty Workflow

```bash
# 1. Run recon
python3 recon/scripts/recon_runner.py target.com

# 2. Feed URLs to scanners
python3 scanners/xss_redirect_scanner.py "https://target.com/search?q=test" \
  --mode xss redirect \
  --output reports/xss.jsonl

# 3. Log in tracker
python3 automation/daily_tracker.py add \
  --program google \
  --target "https://target.com/search?q=test" \
  --type xss \
  --status testing \
  --time 30
```

## PATH Setup

Add to `~/.bashrc`:
```bash
export PATH=$PATH:/home/wasim/go/bin
```

Then:
```bash
source ~/.bashrc
```
