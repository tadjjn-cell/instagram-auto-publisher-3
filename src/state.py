import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_STATE = {"last_message_id": 0}


def load_state(path: str = "data/state.json") -> dict:
    state_file = Path(path)
    if not state_file.exists():
        return dict(DEFAULT_STATE)
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Could not read state file ({e}); starting fresh.")
        return dict(DEFAULT_STATE)


def save_state(state: dict, path: str = "data/state.json") -> None:
    state_file = Path(path)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
