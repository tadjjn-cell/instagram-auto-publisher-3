from telethon import TelegramClient
from telethon.sessions import StringSession


def get_telegram_client(config: dict) -> TelegramClient:
    """Build a Telethon client from a saved session string (no login prompt needed)."""
    return TelegramClient(
        StringSession(config["telegram_session"]),
        config["telegram_api_id"],
        config["telegram_api_hash"],
    )
