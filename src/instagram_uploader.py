import logging
import time

import httpx

logger = logging.getLogger(__name__)

GRAPH_ROOT = "https://graph.instagram.com/v25.0"
TOKEN_LIFETIME_DAYS = 60


def split_token(secret: str) -> tuple[str, int | None]:
    """IG_ACCESS_TOKEN is stored as '<token>|<issued_at_unix>' (issue date is optional)."""
    token, _, issued = secret.partition("|")
    return token.strip(), (int(issued) if issued.strip().isdigit() else None)


def days_until_expiry(issued_at: int | None) -> float | None:
    if issued_at is None:
        return None
    return TOKEN_LIFETIME_DAYS - (time.time() - issued_at) / 86400


def upload_reel(access_token: str, ig_user_id: str, video_url: str, caption: str) -> str:
    """
    Publish a public video URL as an Instagram Reel (Instagram API with Instagram Login).
    Instagram fetches the video itself from video_url (no direct byte upload), so the
    caller must host it at a temporary public URL first. Returns the published media id.
    """
    with httpx.Client(timeout=60) as client:
        create_resp = client.post(
            f"{GRAPH_ROOT}/{ig_user_id}/media",
            data={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": access_token,
            },
        )
        create_data = create_resp.json()
        if "id" not in create_data:
            raise Exception(f"Instagram media container creation failed: {create_data}")
        creation_id = create_data["id"]

        status = None
        status_data: dict = {}
        for _ in range(30):  # up to ~5 minutes
            time.sleep(10)
            status_resp = client.get(
                f"{GRAPH_ROOT}/{creation_id}",
                params={"fields": "status_code", "access_token": access_token},
            )
            status_data = status_resp.json()
            status = status_data.get("status_code")
            if status == "FINISHED":
                break
            if status in ("ERROR", "EXPIRED"):
                raise Exception(f"Instagram failed to process the video: {status_data}")

        if status != "FINISHED":
            raise Exception(f"Instagram video processing timed out (last status: {status_data})")

        publish_resp = client.post(
            f"{GRAPH_ROOT}/{ig_user_id}/media_publish",
            data={"creation_id": creation_id, "access_token": access_token},
        )
        publish_data = publish_resp.json()
        if "id" not in publish_data:
            raise Exception(f"Instagram publish failed: {publish_data}")

        return publish_data["id"]
