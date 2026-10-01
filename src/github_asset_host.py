import logging
import os

import httpx

logger = logging.getLogger(__name__)

API_ROOT = "https://api.github.com"
UPLOAD_ROOT = "https://uploads.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def publish_temp_asset(token: str, repo: str, file_path: str, tag: str) -> dict:
    """
    Upload a file as a GitHub Release asset so it has a public, directly-fetchable
    URL (Instagram's Graph API needs to fetch the video from a public URL -- it has
    no direct byte-upload endpoint like YouTube/TikTok). The repo must be public.

    Returns {"release_id": ..., "asset_url": <public browser_download_url>}.
    """
    with httpx.Client(timeout=120) as client:
        resp = client.post(
            f"{API_ROOT}/repos/{repo}/releases",
            headers=_headers(token),
            json={"tag_name": tag, "name": tag, "draft": False, "prerelease": True},
        )
        resp.raise_for_status()
        release = resp.json()
        release_id = release["id"]

        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            data = f.read()

        upload_resp = client.post(
            f"{UPLOAD_ROOT}/repos/{repo}/releases/{release_id}/assets",
            headers={**_headers(token), "Content-Type": "video/mp4"},
            params={"name": filename},
            content=data,
        )
        upload_resp.raise_for_status()
        asset_url = upload_resp.json()["browser_download_url"]

        return {"release_id": release_id, "asset_url": asset_url, "tag": tag}


def delete_temp_asset(token: str, repo: str, release_id: int, tag: str) -> None:
    """Best-effort cleanup: delete the temporary release and its tag."""
    with httpx.Client(timeout=30) as client:
        try:
            client.delete(f"{API_ROOT}/repos/{repo}/releases/{release_id}", headers=_headers(token))
        except Exception as e:
            logger.warning(f"Could not delete temp release {release_id}: {e}")
        try:
            client.delete(f"{API_ROOT}/repos/{repo}/git/refs/tags/{tag}", headers=_headers(token))
        except Exception as e:
            logger.warning(f"Could not delete temp tag {tag}: {e}")
