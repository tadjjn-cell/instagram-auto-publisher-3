import logging
import os
from telethon import TelegramClient

logger = logging.getLogger(__name__)


def _is_video_message(message) -> bool:
    if message.video:
        return True
    if message.document and message.document.mime_type and "video" in message.document.mime_type:
        return True
    return False


def _resolve_caption(raw_caption: str, config: dict) -> tuple[bool, str]:
    """
    Decide whether this video belongs to this pipeline, and return its cleaned caption.
    Lets several channels share the same Telegram source chat: a "require_tag" pipeline
    only takes captions starting with that tag (tag stripped off); other pipelines list
    that tag in "exclude_tags" so they skip it and leave it for the tagged pipeline.
    """
    telegram_config = config.get("telegram", {})
    require_tag = telegram_config.get("require_tag", "")
    exclude_tags = telegram_config.get("exclude_tags", [])

    if require_tag:
        if not raw_caption.lower().startswith(require_tag.lower()):
            return False, raw_caption
        return True, raw_caption[len(require_tag):].strip(" :-")

    for tag in exclude_tags:
        if raw_caption.lower().startswith(tag.lower()):
            return False, raw_caption

    return True, raw_caption


async def fetch_new_videos(client: TelegramClient, config: dict, state: dict, limit: int) -> list[dict]:
    """
    Scan the source chat for video messages newer than the last processed one.

    Downloads at most `limit` videos per call. State's last_message_id only advances
    past a video once it has actually been downloaded, so a video skipped this run
    (because the limit was reached) will be picked up again on the next run.
    """
    source_chat = config["telegram_source_chat"]
    downloads_dir = config.get("paths", {}).get("downloads_dir", "downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    last_id = state.get("last_message_id", 0)
    highest_seen_id = last_id
    results: list[dict] = []

    async for message in client.iter_messages(source_chat, min_id=last_id, reverse=True):
        if _is_video_message(message):
            should_process, caption = _resolve_caption((message.text or "").strip(), config)
            if not should_process:
                highest_seen_id = message.id
                continue
            if len(results) >= limit:
                logger.info(f"Reached per-run limit ({limit}); message {message.id} will be picked up next run.")
                break
            logger.info(f"Downloading video from message {message.id}...")
            file_path = await message.download_media(file=f"{downloads_dir}/")
            if not file_path:
                logger.warning(f"Failed to download media for message {message.id}; skipping.")
                highest_seen_id = message.id
                continue
            results.append(
                {
                    "message_id": message.id,
                    "caption": caption,
                    "file_path": file_path,
                }
            )
            highest_seen_id = message.id
        else:
            highest_seen_id = message.id

    state["last_message_id"] = highest_seen_id
    return results
