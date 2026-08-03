#!/usr/bin/env python3
"""Scan runner wrapper — calls the actual scanner and logs results."""
import argparse
import subprocess
import sys
from pathlib import Path

SCANNER = Path(__file__).resolve().parent.parent / "scanners" / "xss_redirect_scanner.py"


def main():
    parser = argparse.ArgumentParser(description="Bug bounty scan runner")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--mode", nargs="+", default=["xss", "redirect"])
    parser.add_argument("--output", default="reports/scan_results.jsonl")
    args = parser.parse_args()

    if not SCANNER.exists():
        print(f"Scanner not found: {SCANNER}")
        sys.exit(1)

    cmd = [
        sys.executable,
        str(SCANNER),
        args.url,
        "--mode",
    ] + args.mode + [
        "--output", args.output,
    ]
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
