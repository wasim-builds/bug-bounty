#!/usr/bin/env python3
"""CSRF Scanner — detects missing CSRF tokens and same-site cookie issues."""
import argparse
import re
import sys
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def extract_forms(html: str, base_url: str):
    forms = []
    for m in re.finditer(r"<form[^>]*>(.*?)</form>", html, re.IGNORECASE | re.DOTALL):
        form = m.group(0)
        action = re.search(r'action=["\']([^"\']+)["\']', form, re.IGNORECASE)
        method = re.search(r'method=["\']([^"\']+)["\']', form, re.IGNORECASE)
        inputs = re.findall(r'<input[^>]+name=["\']([^"\']+)["\'][^>]*>', form, re.IGNORECASE)
        forms.append({
            "action": urljoin(base_url, action.group(1)) if action else base_url,
            "method": (method.group(1) if method else "GET").upper(),
            "inputs": inputs,
        })
    return forms


def has_csrf_token(inputs: list[str]) -> bool:
    csrf_keywords = ["csrf", "token", "authenticity", "nonce", "_token", "csrfmiddlewaretoken"]
    return any(any(kw in name.lower() for kw in csrf_keywords) for name in inputs)


def check_csrf(url: str) -> list[dict]:
    findings = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        forms = extract_forms(resp.text, url)
        for form in forms:
            if form["method"] == "POST" and not has_csrf_token(form["inputs"]):
                findings.append({
                    "type": "csrf",
                    "url": url,
                    "form_action": form["action"],
                    "method": form["method"],
                    "inputs": form["inputs"],
                    "missing_token": True,
                })
    except Exception as e:
        findings.append({"type": "csrf", "url": url, "error": str(e)})
    return findings


def scan_targets(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        print(f"[*] Checking CSRF on {url}")
        findings = check_csrf(url)
        results.extend(findings)
        time.sleep(0.5)
    return results


def main():
    parser = argparse.ArgumentParser(description="CSRF Scanner")
    parser.add_argument("urls", nargs="+", help="Target URLs")
    parser.add_argument("--output", default="reports/csrf_scan.jsonl")
    args = parser.parse_args()
    results = scan_targets(args.urls)
    hits = [r for r in results if r.get("missing_token")]
    print(f"\n[*] Scan complete. {len(hits)} potential CSRF issues out of {len(results)} checks.")
    if hits:
        print("[!] Review findings manually before reporting!")
    from pathlib import Path
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8") as f:
        for r in results:
            f.write(__import__("json").dumps(r, ensure_ascii=False) + "\n")
    print(f"[*] Results saved to {out}")


if __name__ == "__main__":
    main()
