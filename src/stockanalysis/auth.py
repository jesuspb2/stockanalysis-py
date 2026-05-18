"""
CLI authentication for stockanalysis.com Pro accounts.

Set SA_EMAIL and SA_PASSWORD in a .env file at the repo root, then run:
    stockanalysis-login

The session state is saved to .auth/state.json and reused in all requests.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from stockanalysis.core.session import STATE_PATH

LOGIN_URL = "https://stockanalysis.com/login/"


def save_session(path: Path | str | None = None) -> None:
    from playwright.sync_api import sync_playwright

    load_dotenv()
    email = os.getenv("SA_EMAIL")
    password = os.getenv("SA_PASSWORD")

    if not email or not password:
        print("SA_EMAIL and SA_PASSWORD must be set in your .env file.")
        sys.exit(1)

    state_path = Path(path) if path else STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LOGIN_URL)

        try:
            page.get_by_role("button", name="Consent").click(timeout=3000)
        except Exception:
            pass

        page.get_by_role("textbox", name="Email address").fill(email)
        page.get_by_role("textbox", name="Password").fill(password)
        page.get_by_role("button", name="Log In").click()

        page.wait_for_url(lambda url: "/login" not in url, timeout=15000)

        state = context.storage_state()
        state_path.write_text(json.dumps(state, indent=2))
        browser.close()

    print(f"Session saved to {state_path}")


def main() -> None:
    save_session()


if __name__ == "__main__":
    main()
