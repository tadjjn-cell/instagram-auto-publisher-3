"""
Run this ONCE on your own PC to log in to your Telegram account and generate a
session string. Paste the printed string into the TELEGRAM_SESSION secret.

This never needs to run again unless you log out of that session.
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print("Get your API_ID and API_HASH for free at https://my.telegram.org (API Development Tools).\n")

api_id = int(input("API_ID: ").strip())
api_hash = input("API_HASH: ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    session_string = client.session.save()
    print("\n=== COPY THIS SESSION STRING — KEEP IT SECRET ===\n")
    print(session_string)
    print("\n===================================================")
    print("Save it as the TELEGRAM_SESSION secret (and TELEGRAM_API_ID / TELEGRAM_API_HASH too).")
