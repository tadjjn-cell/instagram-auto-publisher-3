import os
import asyncio
import logging
from pathlib import Path

import yaml
from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError, APITimeoutError, APIConnectionError

load_dotenv()
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load config.yaml and merge in secrets from environment variables."""
    load_dotenv()

    config_file = Path(config_path)
    config: dict = {}
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    config["groq_api_key"] = _require_env("GROQ_API_KEY")

    config["telegram_api_id"] = int(_require_env("TELEGRAM_API_ID"))
    config["telegram_api_hash"] = _require_env("TELEGRAM_API_HASH")
    config["telegram_session"] = _require_env("TELEGRAM_SESSION")
    source_chat = os.getenv("TELEGRAM_SOURCE_CHAT") or config.get("telegram", {}).get("source_chat", "")
    config["telegram_source_chat"] = _parse_chat_id(source_chat)

    config["ig_access_token"] = _require_env("IG_ACCESS_TOKEN")
    config["ig_user_id"] = _require_env("IG_USER_ID")

    # Used to host the video at a temporary public URL (GitHub Release asset) so
    # Instagram's Graph API can fetch it -- auto-provided inside GitHub Actions.
    config["github_token"] = _require_env("GITHUB_TOKEN")
    config["github_repository"] = _require_env("GITHUB_REPOSITORY")

    return config


def _parse_chat_id(value: str):
    """Telethon needs an int for numeric chat/channel ids, not a str."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return value


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_groq_client(config: dict) -> AsyncOpenAI:
    """Create a Groq client (OpenAI-compatible, free tier)."""
    return AsyncOpenAI(api_key=config["groq_api_key"], base_url="https://api.groq.com/openai/v1")


async def call_groq_with_retry(client: AsyncOpenAI, max_retries: int = 3, **kwargs) -> str:
    """Call Groq chat completion with exponential backoff on transient errors."""
    for attempt in range(max_retries):
        try:
            response = await client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except RateLimitError:
            wait = 2 ** (attempt + 1)
            logger.warning(f"Groq rate limited. Waiting {wait}s (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(wait)
        except APITimeoutError:
            logger.warning(f"Groq timeout (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(1)
        except APIConnectionError as e:
            logger.warning(
                f"Groq connection error ({e.__cause__!r}). Waiting 5s (attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(5)

    raise Exception(f"Groq API failed after {max_retries} retries")
