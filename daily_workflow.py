#!/usr/bin/env python3
"""Daily Bug Bounty Workflow — 3 step startup routine."""
import subprocess
import sys
from pathlib import Path

BASE = Path.home() / "bug-bounty"
PYTHON = sys.executable


def run(cmd: list[str]):
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd)


def main():
    print("=" * 50)
    print("🐛 Daily Bug Bounty Workflow")
    print("=" * 50)

    # Step 1: Check status
    print("\n📊 STEP 1: Check yesterday's activity")
    print("-" * 50)
    run([PYTHON, str(BASE / "automation/daily_tracker.py"), "today"])
    run([PYTHON, str(BASE / "automation/daily_tracker.py"), "week"])

    # Step 2: Run recon on a target
    print("\n🔍 STEP 2: Recon a target")
    print("-" * 50)
    target = input("Enter target domain (or press Enter to skip): ").strip()
    if target:
        run([PYTHON, str(BASE / "recon/scripts/recon_runner.py"), target, "--skip-nuclei"])
    else:
        print("Skipping recon.")

    # Step 3: Scan for bugs
    print("\n🛠️  STEP 3: Scan for bugs")
    print("-" * 50)
    url = input("Enter URL to scan (with query params) or press Enter to skip: ").strip()
    if url:
        run([
            PYTHON, str(BASE / "automation/master_scanner.py"), url,
            "--modes", "xss", "redirect", "csrf", "ssrf", "auth", "sqli",
            "--output-dir", str(BASE / "reports")
        ])
    else:
        print("Skipping scan.")

    print("\n" + "=" * 50)
    print("✅ Daily workflow complete.")
    print("=" * 50)
    print("\nNext: Review reports/, log results in daily_tracker, submit valid findings.")


if __name__ == "__main__":
    main()
