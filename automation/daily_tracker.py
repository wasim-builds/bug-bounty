#!/usr/bin/env python3
"""Daily Bug Bounty Hunter Tracker.

Logs daily hunting activity, tracks time spent, and generates reports.
"""
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "daily-logs"
PROGRAMS_DIR = BASE_DIR / "programs"
REPORTS_DIR = BASE_DIR / "reports"


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def log_path(date: str) -> Path:
    return LOGS_DIR / f"{date}.jsonl"


def ensure_log(date: str) -> Path:
    p = log_path(date)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def add_entry(
    date: str,
    program: str,
    target: str,
    bug_type: str,
    status: str,
    notes: str = "",
    time_minutes: int = 0,
) -> dict:
    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": date,
        "program": program.strip().lower(),
        "target": target.strip(),
        "bug_type": bug_type.strip().lower(),
        "status": status.strip().lower(),
        "notes": notes.strip(),
        "time_minutes": time_minutes,
    }
    p = ensure_log(date)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def show_day(date: str):
    p = log_path(date)
    if not p.exists():
        print(f"No entries for {date}")
        return
    entries = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"\n=== {date} ===")
    print(f"Total entries: {len(entries)}")
    total_time = sum(e.get("time_minutes", 0) for e in entries)
    print(f"Total time: {total_time // 60}h {total_time % 60}m")
    
    status_counts = {}
    for e in entries:
        status_counts[e["status"]] = status_counts.get(e["status"], 0) + 1
    print("Status breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
        
    print("\nEntries:")
    for e in entries:
        print(f"  [{e['bug_type']}] {e['program']} / {e['target']} -> {e['status']} ({e.get('time_minutes', 0)}m)")
        if e.get("notes"):
            print(f"    Notes: {e['notes'][:100]}")


def show_week():
    today = datetime.now().date()
    entries = []
    for i in range(7):
        d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        p = log_path(d)
        if p.exists():
            entries.extend(json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip())
    print(f"\n=== Last 7 days ===")
    print(f"Total entries: {len(entries)}")
    total_time = sum(e.get("time_minutes", 0) for e in entries)
    print(f"Total time: {total_time // 60}h {total_time % 60}m")
    
    status_counts = {}
    for e in entries:
        status_counts[e["status"]] = status_counts.get(e["status"], 0) + 1
    print("Status breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
        
    by_program = {}
    for e in entries:
        by_program[e["program"]] = by_program.get(e["program"], 0) + 1
    print("By program:")
    for prog, count in sorted(by_program.items(), key=lambda x: -x[1]):
        print(f"  {prog}: {count}")


def generate_report(date: str):
    p = log_path(date)
    if not p.exists():
        print(f"No data for {date}")
        return
    entries = [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    report_path = REPORTS_DIR / f"report_{date}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    total_time = sum(e.get("time_minutes", 0) for e in entries)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Bug Bounty Daily Report — {date}\n\n")
        f.write(f"**Total time:** {total_time // 60}h {total_time % 60}m\n\n")
        f.write(f"**Total targets tested:** {len(entries)}\n\n")
        status_counts = {}
        for e in entries:
            status_counts[e["status"]] = status_counts.get(e["status"], 0) + 1
        f.write("## Status Breakdown\n\n")
        for status, count in sorted(status_counts.items()):
            f.write(f"- {status}: {count}\n")
        f.write("\n## Targets\n\n")
        for e in entries:
            f.write(f"- [{e['bug_type']}] **{e['program']}** / {e['target']} -> {e['status']} ({e.get('time_minutes', 0)}m)\n")
            if e.get("notes"):
                f.write(f"  - Notes: {e['notes']}\n")
    print(f"Report saved: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Daily Bug Bounty Tracker")
    sub = parser.add_subparsers(dest="command")

    # add command
    p_add = sub.add_parser("add", help="Add hunting entry")
    p_add.add_argument("-p", "--program", required=True, help="Program name (e.g. google, hackerone, private-target)")
    p_add.add_argument("-t", "--target", required=True, help="Target URL/domain/endpoint")
    p_add.add_argument("-b", "--type", default="other", help="Vulnerability or task type (e.g. xss, idor, recon)")
    p_add.add_argument(
        "-s",
        "--status",
        default="testing",
        choices=["testing", "needs-poc", "submitted", "duplicate", "not-a-bug", "accepted", "paid", "closed"],
        help="Current workflow status (default: testing)",
    )
    p_add.add_argument("-n", "--notes", default="", help="Additional notes or PoC details")
    p_add.add_argument("-m", "--time", type=int, default=0, help="Time spent in minutes (default: 0)")
    p_add.add_argument("-d", "--date", default=today_str(), help="Date in YYYY-MM-DD format (default: today)")

    # query subcommands
    sub.add_parser("today", help="Show today's entries")
    
    p_day = sub.add_parser("day", help="Show entries for a specific date")
    p_day.add_argument("-d", "--date", default=today_str(), help="Date in YYYY-MM-DD format (default: today)")

    sub.add_parser("week", help="Show last 7 days summary")
    
    p_rep = sub.add_parser("report", help="Generate Markdown daily report")
    p_rep.add_argument("-d", "--date", default=today_str(), help="Date in YYYY-MM-DD format (default: today)")

    args = parser.parse_args()

    if args.command == "add":
        entry = add_entry(args.date, args.program, args.target, args.type, args.status, args.notes, args.time)
        print(f"Logged [{entry['date']}]: [{entry['bug_type']}] {entry['program']} / {entry['target']} -> {entry['status']}")
    elif args.command == "today":
        show_day(today_str())
    elif args.command == "day":
        show_day(args.date)
    elif args.command == "week":
        show_week()
    elif args.command == "report":
        generate_report(args.date)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()