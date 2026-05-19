from __future__ import annotations

import json
import os
import threading
from pathlib import Path

import httpx

STATE_PATH = (
    Path(os.environ["SA_STATE_PATH"])
    if "SA_STATE_PATH" in os.environ
    else Path.cwd() / ".auth" / "state.json"
)

_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}

_session: httpx.Client | None = None
_session_lock = threading.Lock()


def get_session() -> httpx.Client:
    global _session
    if _session is None:
        with _session_lock:
            if _session is None:
                _session = _build_session()
    return _session


def _build_session() -> httpx.Client:
    cookies: dict[str, str] = {}
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text())
        for cookie in state.get("cookies", []):
            cookies[cookie["name"]] = cookie["value"]

    return httpx.Client(
        headers=_DEFAULT_HEADERS, cookies=cookies, follow_redirects=True
    )
