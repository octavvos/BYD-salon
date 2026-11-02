import json
import logging
import threading
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def _post(url: str, payload: dict) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(request, timeout=5)
    except Exception:  # xabarnoma yiqilsa ham ariza saqlanib qoladi
        logger.exception("Telegram xabarnomasi yuborilmadi")


def send_telegram(text: str) -> None:
    """Token sozlangan bo'lsa, xabarni fon oqimida yuboradi."""
    token, chat_id = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if not (token and chat_id):
        return
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    threading.Thread(target=_post, args=(url, payload), daemon=True).start()
