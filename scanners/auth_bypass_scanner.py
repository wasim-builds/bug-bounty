#!/usr/bin/env python3
"""Auth Bypass Scanner — detects broken authentication and authorization."""
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


def check_idor(url: str, original_id: str = "1", test_id: str = "2") -> dict:
    """Check for insecure direct object references."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    for param in list(params.keys()):
        if "id" in param.lower() and params[param][0] == original_id:
            params[param] = [test_id]
            new_query = urlencode(params, doseq=True)
            test_url = parsed._replace(query=new_query).geturl()
            try:
                resp_orig = requests.get(url, headers=HEADERS, timeout=15)
                resp_test = requests.get(test_url, headers=HEADERS, timeout=15)
                if resp_test.status_code == 200 and resp_orig.status_code == 200:
                    if resp_test.text != resp_orig.text:
                        return {
                            "type": "idor",
                            "url": test_url,
                            "param": param,
                            "original": original_id,
                            "test": test_id,
                            "potential": True,
                        }
            except Exception as e:
                return {"type": "idor", "url": test_url, "error": str(e)}
    return {"type": "idor", "url": url, "potential": False}


def check_auth_bypass(url: str) -> list[dict]:
    findings = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=False)
        if resp.status_code in (301, 302, 303, 307, 308):
            location = resp.headers.get("Location", "")
            if "login" not in location.lower() and "auth" not in location.lower():
                findings.append({
                    "type": "auth_bypass",
                    "url": url,
                    "redirect": location,
                    "potential": True,
                })
    except Exception as e:
        findings.append({"type": "auth_bypass", "url": url, "error": str(e)})
    return findings


def scan_targets(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        print(f"[*] Checking auth bypass on {url}")
        results.extend(check_auth_bypass(url))
        idor = check_idor(url)
        if idor.get("potential"):
            results.append(idor)
        time.sleep(0.5)
    return results


def main():
    parser = argparse.ArgumentParser(description="Auth Bypass Scanner")
    parser.add_argument("urls", nargs="+", help="Target URLs")
    parser.add_argument("--output", default="reports/auth_bypass_scan.jsonl")
    args = parser.parse_args()
    results = scan_targets(args.urls)
    hits = [r for r in results if r.get("potential")]
    print(f"\n[*] Scan complete. {len(hits)} potential auth issues out of {len(results)} checks.")
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
