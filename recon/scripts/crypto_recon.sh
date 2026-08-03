#!/bin/bash
# Crypto.com Quick Recon Script
# Run this from your local machine

echo "=== Crypto.com Bug Bounty Recon ==="
echo "Program: https://hackerone.com/crypto"
echo "Bounty: \$1 - \$1,000,000"
echo ""

# Create output dir
mkdir -p recon/output/crypto.com
cd recon/output/crypto.com

echo "[1/5] Enumerating subdomains..."
subfinder -d crypto.com -o subfinder.txt -silent
amass enum -d crypto.com -o amass.txt
cat subfinder.txt amass.txt | sort -u > all_subdomains.txt
echo "Found $(wc -l < all_subdomains.txt) subdomains"

echo ""
echo "[2/5] Probing for alive hosts..."
cat all_subdomains.txt | httpx -silent -status-code -title -tech-detect -o alive.txt
echo "Found $(wc -l < alive.txt) alive hosts"

echo ""
echo "[3/5] Crawling for URLs..."
cat alive.txt | cut -d' ' -f1 | katana -silent -depth 2 -timeout 10 -o urls.txt 2>/dev/null || echo "Katana skipped"
echo "Found $(wc -l < urls.txt) URLs"

echo ""
echo "[4/5] Extracting parameters..."
if [ -f urls.txt ]; then
    cat urls.txt | unfurl keys > parameters.txt
    echo "Found $(wc -l < parameters.txt) unique parameters"
fi

echo ""
echo "[5/5] Running nuclei..."
if [ -f urls.txt ]; then
    nuclei -l urls.txt -o nuclei_results.txt -silent -severity low,medium,high,critical 2>/dev/null || echo "Nuclei skipped"
    echo "Nuclei findings: $(wc -l < nuclei_results.txt 2>/dev/null || echo 0)"
fi

echo ""
echo "=== Recon complete ==="
echo "Results in: recon/output/crypto.com/"
echo ""
echo "Next steps:"
echo "1. Review alive.txt for interesting endpoints"
echo "2. Check parameters.txt for redirect/query params"
echo "3. Test manually with: python3 ../../automation/master_scanner.py <url> --modes xss redirect"
echo "4. Draft report if you find something"
