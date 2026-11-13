# Telegram Alert — Key Functions
# Shows: HTML message building, retry logic, rate limit handling

import html
import time
import logging
from datetime import datetime

import requests

log = logging.getLogger(__name__)

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

LEVEL = {
    "critical": "🔴 CRITICAL",
    "error":    "🟠 ERROR",
    "warning":  "🟡 WARNING",
}


def build_text(
    service: str,
    message: str,
    level: str = "error",
    trace: str | None = None,
    event_id: str | int | None = None,
) -> str:
    """Build HTML-formatted alert message with optional traceback."""
    t = datetime.now().astimezone()
    head = LEVEL.get(level, LEVEL["error"])

    lines = [
        f"<b>{head}</b> · <code>{html.escape(service)}</code>",
        "",
        html.escape(message),
    ]

    lines.append(f"\n🕐 {t:%d.%m.%Y %H:%M:%S}")

    if trace:
        tb = trace.strip()
        if len(tb) > 3000:  # Telegram limit 4096
            tb = "…" + tb[-3000:]
        lines.append(f"\n<pre>{html.escape(tb)}</pre>")

    if event_id is not None:
        lines.append(f"\n<i>id:</i> <code>{html.escape(str(event_id))}</code>")

    return "\n".join(lines)


def send_alert(
    text: str,
    keyboard: list | None = None,
    retries: int = 3,
) -> dict | None:
    """Send Telegram alert with retry and rate limit handling."""
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if keyboard:
        payload["reply_markup"] = {"inline_keyboard": keyboard}

    for attempt in range(1, retries + 1):
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json=payload,
                timeout=10,
            )
        except requests.RequestException as e:
            log.warning("network error %s/%s: %s", attempt, retries, e)
            time.sleep(2 ** attempt)
            continue

        if r.status_code == 200:
            return r.json()["result"]

        if r.status_code == 429:  # rate limit
            wait = r.json().get("parameters", {}).get("retry_after", 3)
            log.warning("rate limited, sleep %ss", wait)
            time.sleep(wait)
            continue

        log.error("sendMessage failed: %s %s", r.status_code, r.text[:300])
        if 400 <= r.status_code < 500:  # client error — retry won't help
            return None
        time.sleep(2 ** attempt)

    log.error("give up after %s attempts", retries)
    return None
