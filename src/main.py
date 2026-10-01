import asyncio
import logging
import os
import time

from src.config import load_config
from src.state import load_state, save_state
from src.telegram_client import get_telegram_client
from src.telegram_source import fetch_new_videos
from src.trends import get_trending_queries
from src.caption_generator import generate_instagram_caption
from src.github_asset_host import publish_temp_asset, delete_temp_asset
from src.instagram_uploader import upload_reel, split_token, days_until_expiry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def build_caption(caption: str, hashtags: list[str]) -> str:
    if not hashtags:
        return caption
    tag_line = " ".join(f"#{h.replace(' ', '')}" for h in hashtags)
    return f"{caption}\n\n{tag_line}"


async def notify(client, chat, text: str) -> None:
    try:
        await client.send_message(chat, text)
    except Exception as e:
        logger.warning(f"Could not send Telegram notification: {e}")


async def main() -> None:
    config = load_config()
    state_path = config.get("paths", {}).get("state_file", "data/state.json")
    state = load_state(state_path)

    post_interval_hours = config.get("schedule", {}).get("post_interval_hours", 0)
    if post_interval_hours > 0:
        elapsed_hours = (time.time() - state.get("last_upload_time", 0)) / 3600
        if elapsed_hours < post_interval_hours:
            remaining = post_interval_hours - elapsed_hours
            logger.info(f"Drip-feed schedule active: next post in {remaining:.1f}h. Skipping this run.")
            return
        fetch_limit = 1
    else:
        fetch_limit = config.get("limits", {}).get("max_uploads_per_run", 3)

    client = get_telegram_client(config)
    await client.start()

    try:
        ig_token, issued_at = split_token(config["ig_access_token"])
        remaining = days_until_expiry(issued_at)
        today = time.strftime("%Y-%m-%d")
        if remaining is not None and remaining < 15 and state.get("ig_last_expiry_warning") != today:
            await notify(
                client,
                config["telegram_source_chat"],
                f"⏰ Instagram token expires in ~{max(remaining, 0):.0f} days. Re-run "
                "setup/get_instagram_token.py and update the IG_ACCESS_TOKEN secret.",
            )
            state["ig_last_expiry_warning"] = today

        videos = await fetch_new_videos(client, config, state, limit=fetch_limit)

        if not videos:
            logger.info("No new videos found.")
            return

        source_chat = config["telegram_source_chat"]
        max_trending = config.get("keywords", {}).get("max_trending", 10)
        github_token = config["github_token"]
        github_repo = config["github_repository"]

        for video in videos:
            topic = video["caption"] or "video"
            logger.info(f"Processing message {video['message_id']}: topic='{topic}'")
            asset = None
            try:
                trending = await asyncio.to_thread(get_trending_queries, topic, max_trending)
                result = await generate_instagram_caption(topic, trending, config)
                caption = build_caption(result["caption"], result["hashtags"])

                tag = f"ig-temp-{video['message_id']}"
                asset = await asyncio.to_thread(
                    publish_temp_asset, github_token, github_repo, video["file_path"], tag
                )

                media_id = await asyncio.to_thread(
                    upload_reel, ig_token, config["ig_user_id"], asset["asset_url"], caption
                )

                logger.info(f"Published to Instagram: {media_id}")
                await notify(client, source_chat, f"✅ Posted to Instagram:\n{caption[:200]}")

            except Exception as e:
                logger.error(f"Failed to process message {video['message_id']}: {e}")
                await notify(
                    client,
                    source_chat,
                    f"⚠️ Failed to publish Instagram video (message {video['message_id']}): {e}",
                )
            finally:
                if asset:
                    await asyncio.to_thread(
                        delete_temp_asset, github_token, github_repo, asset["release_id"], asset["tag"]
                    )
                state["last_upload_time"] = time.time()
                if os.path.exists(video["file_path"]):
                    os.remove(video["file_path"])

    finally:
        save_state(state, state_path)
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
