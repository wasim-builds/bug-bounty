# Contributing to bug-bounty

Thanks for contributing! This workspace is an automated daily bug bounty
hunting tracker, set of custom scanners, and program scope reference. The
guidelines below cover the conventions used across the repo so that your
changes fit in cleanly.

## Quick Start

```bash
git clone https://github.com/wasim-builds/bug-bounty.git
cd bug-bounty
python3 scanners/sqli_scanner.py "https://target.com/search?q=test"
```

All scripts use the standard library plus `requests`. There is no
`requirements.txt` yet, but if you add new dependencies list them there.

## Repository Structure

```text
automation/   # Cron entrypoint, daily tracker, scan wrapper
scanners/     # Custom vulnerability scanners (one bug class per file)
programs/     # Program scope docs, one folder per program
daily-logs/   # JSONL hunting logs, named YYYY-MM-DD.jsonl
reports/      # Generated Markdown daily reports
logs/         # Automation / cron logs
recon/        # Recon data
telegram-bot/ # Optional Telegram notification bot
tools/        # Helper scripts
```

## Coding Conventions

- **Python 3.9+**: type hints are used throughout (`list[str]`, `dict`, etc.).
  Do not use `typing.List` / `typing.Dict` unless you must support 3.8.
- **Entry point**: every CLI scanner exposes a `main()` guarded by
  `if __name__ == "__main__":` and uses `argparse`.
- **argparse style**: positional `url` first, then `--mode` / `--output`,
  `--max-params`, etc.
- **No comments unless asked**: functions should be self-documenting.
  Module docstrings are fine.
- **Output**: scanners print human-readable `[*]` / `[!]` / `[POTENTIAL ...]`
  progress lines and write JSONL results to `--output`.

## Adding a Scanner

1. Create `scanners/<bug_class>_scanner.py` (e.g. `idor_scanner.py`).
2. Follow the existing pattern in `scanners/sqli_scanner.py`:
   - CLI via `argparse`.
   - Results are dicts written as JSONL to `--output`.
   - Potential hits print a `[POTENTIAL ...]` line.
3. Document the new scanner in the "Scanners" table in `README.md`.
4. If it can be driven by the master runner, wire it into
   `automation/master_scanner.py`.

## Adding a Bug Class

The tracker uses a fixed set of `choices`. If you add a new bug class:
1. Add it to `--type` in `automation/daily_tracker.py`.
2. Add it to the "Bug types" list in `README.md`.
3. Add a matching scanner under `scanners/`.

## Adding a Program Scope

1. Create `programs/<program>/scope.md` (e.g. `programs/google/scope.md`).
2. Use the format: `# <Vendor> <Program> Scope`, then `## In Scope`,
   `## Out of Scope`, `## Rewards`, `## Quick Targets`.
3. Add an entry to the "Programs Reference" table in `README.md`.

## Logging & Reporting Workflow

```bash
# Log a hunting session
python3 automation/daily_tracker.py add \
  --program google --target "https://www.google.com/search?q=test" \
  --type xss --status testing --notes "Testing search param" --time 30

# Review
python3 automation/daily_tracker.py today
python3 automation/daily_tracker.py week

# Generate a daily Markdown report
python3 automation/daily_tracker.py report    # -> reports/report_YYYY-MM-DD.md
```

Daily logs are JSONL keyed by date. Keep entries factual and do **not**
include live API keys, internal IPs, or other secrets in log/note fields.

## Pull Request Guidelines

- **One concern per PR**: a single scanner, a single bug class, or a single
  program scope doc. Do not mix unrelated changes.
- **Keep branches short-lived**: branch from `main`, open the PR promptly,
  and update from `main` if it drifts.
- **Tests**: scanners are scripts; verify by running them against a harmless
  target and confirming JSONL output is valid:
  ```bash
  python3 scanners/sqli_scanner.py "https://example.com?q=test" --output /tmp/out.jsonl
  python3 -c "import json; [json.loads(l) for l in open('/tmp/out.jsonl') if l.strip()]"
  ```
  If you add a reusable module function, add a `tests/` entry where plausible.
- **Docs**: update `README.md` whenever you add a scanner, bug type, or
  program so the reference tables stay in sync.
- **Lint**: Python files are `python3 -m py_compile <file>` clean.

## Security

- Never commit secrets, API keys, or `.env` contents. The repo has a `.env`
  file for local secrets — it must stay out of any PR (add it to `.gitignore`
  if missing).
- Only scan targets you own or that have an active bounty / authorization.
- Do not store raw vulnerability payloads that could be misused in public
  logs without redacting sensitive values.

## Reporting Issues

- Use the GitHub issue tracker for bugs in the scanners, tracker, or docs.
- For new bounty programs: open an issue with the scope link and add a
  `programs/<program>/scope.md` yourself — PRs are welcome.

Happy hunting!
