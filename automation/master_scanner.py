#!/usr/bin/env python3
"""Master scanner runner — runs multiple scanner types on one or more URLs."""
import argparse
import subprocess
import sys
from pathlib import Path

SCANNERS_DIR = Path(__file__).resolve().parent.parent / "scanners"
SCANNERS = {
    "xss": SCANNERS_DIR / "xss_redirect_scanner.py",
    "redirect": SCANNERS_DIR / "xss_redirect_scanner.py",
    "csrf": SCANNERS_DIR / "csrf_scanner.py",
    "ssrf": SCANNERS_DIR / "ssrf_scanner.py",
    "auth": SCANNERS_DIR / "auth_bypass_scanner.py",
    "sqli": SCANNERS_DIR / "sqli_scanner.py",
}


def run_scanner(scanner: Path, args: list[str]) -> int:
    cmd = [sys.executable, str(scanner)] + args
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Master Scanner Runner")
    parser.add_argument("urls", nargs="+", help="Target URLs")
    parser.add_argument("--modes", nargs="+", default=["xss", "redirect", "csrf", "ssrf", "auth", "sqli"])
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()

    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for mode in args.modes:
        scanner = SCANNERS.get(mode)
        if not scanner:
            print(f"[!] Unknown mode: {mode}")
            continue
        print(f"\n=== Running {mode.upper()} scanner ===")
        out_file = output_dir / f"{mode}_scan_{timestamp}.jsonl"
        if mode in ("xss", "redirect"):
            for url in args.urls:
                run_scanner(scanner, [url, "--mode", mode, "--output", str(out_file)])
        elif mode == "csrf":
            run_scanner(scanner, args.urls + ["--output", str(out_file)])
        elif mode == "ssrf":
            for url in args.urls:
                run_scanner(scanner, [url, "--output", str(out_file)])
        elif mode == "auth":
            run_scanner(scanner, args.urls + ["--output", str(out_file)])
        elif mode == "sqli":
            for url in args.urls:
                run_scanner(scanner, [url, "--output", str(out_file)])
        print(f"[*] {mode.upper()} results saved to {out_file}")


if __name__ == "__main__":
    main()
