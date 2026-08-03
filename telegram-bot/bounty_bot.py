#!/usr/bin/env python3
"""Telegram Bot — alerts for new bounty programs and daily hunt reminders."""
import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("[!] requests not installed. Run: pip install requests")
    sys.exit(1)

CONFIG_PATH = Path.home() / ".bug_bounty_telegram.json"
BOT_TOKEN = os.getenv("BB_TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("BB_TELEGRAM_CHAT_ID", "")


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def save_config(cfg: dict):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def send_telegram(text: str, chat_id: str = "", bot_token: str = "") -> bool:
    cfg = load_config()
    token = bot_token or cfg.get("bot_token", "")
    cid = chat_id or cfg.get("chat_id", "")
    if not token or not cid:
        print("[!] Missing bot_token or chat_id. Run setup first.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": cid, "text": text, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            print("[+] Telegram message sent")
            return True
        print(f"[!] Telegram error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[!] Telegram failed: {e}")
    return False


def setup():
    print("=== Telegram Bot Setup ===")
    print("\nStep 1: Create a bot")
    print("  1. Open Telegram, search @BotFather")
    print("  2. Send: /newbot")
    print("  3. Follow prompts, copy the token (starts with 123456:ABC-DEF...)")
    token = input("\nPaste bot token: ").strip()
    print("\nStep 2: Get your chat ID")
    print("  1. Open Telegram, search @userinfobot")
    print("  2. Send any message")
    print("  3. Copy your numeric chat ID")
    chat_id = input("\nPaste chat ID: ").strip()
    cfg = {"bot_token": token, "chat_id": chat_id}
    save_config(cfg)
    print(f"\n[+] Config saved to {CONFIG_PATH}")
    ok = send_telegram("🐛 Bug bounty bot activated! You will receive alerts here.", chat_id=chat_id, bot_token=token)
    if ok:
        print("[+] Test message sent. Check Telegram.")
    else:
        print("[!] Test message failed. Check token/chat ID.")


def test():
    cfg = load_config()
    if not cfg:
        print("[!] No config found. Run setup first.")
        return
    send_telegram("✅ Test alert from bug bounty bot.")


def alert_new_program(program_name: str, url: str, payout: str = ""):
    text = f"🆕 *New Bounty Program*\n\n"
    text += f"*Program:* {program_name}\n"
    text += f"*URL:* {url}\n"
    if payout:
        text += f"*Payout:* {payout}\n"
    text += f"\n🔗 [View Program]({url})"
    send_telegram(text)


def daily_reminder():
    text = "⏰ *Daily Hunt Reminder*\n\n"
    text += "1. Run: `bounty-start`\n"
    text += "2. Pick one target from `targets.txt`\n"
    text += "3. Run recon + scanners\n"
    text += "4. Log results in tracker\n"
    text += "5. Submit valid findings\n\n"
    text += "💪 Consistent daily hunting > sporadic marathons."
    send_telegram(text)


def main():
    parser = argparse.ArgumentParser(description="Telegram Bot for Bug Bounty Alerts")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup", help="Configure bot token and chat ID")
    sub.add_parser("test", help="Send test message")
    sub.add_parser("daily", help="Send daily reminder")

    p_alert = sub.add_parser("alert", help="Send new program alert")
    p_alert.add_argument("--program", required=True)
    p_alert.add_argument("--url", required=True)
    p_alert.add_argument("--payout", default="")

    args = parser.parse_args()

    if args.command == "setup":
        setup()
    elif args.command == "test":
        test()
    elif args.command == "daily":
        daily_reminder()
    elif args.command == "alert":
        alert_new_program(args.program, args.url, args.payout)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
