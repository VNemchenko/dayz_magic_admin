from __future__ import annotations

import logging
from typing import Optional

import requests

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    """Sends messages to a Telegram chat via bot API."""

    def __init__(self, bot_token: str, chat_id: str):
        self._bot_token = bot_token
        self._chat_id = chat_id

    @property
    def api_url(self) -> str:
        return f"https://api.telegram.org/bot{self._bot_token}/sendMessage"

    def send(self, message: str, parse_mode: Optional[str] = None) -> None:
        payload = {"chat_id": self._chat_id, "text": message}
        if parse_mode:
            payload["parse_mode"] = parse_mode

        LOGGER.debug("Sending Telegram notification")
        response = requests.post(self.api_url, json=payload, timeout=15)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            LOGGER.error("Failed to send Telegram notification: %s", response.text)
            raise
        LOGGER.info("Sent Telegram notification")


__all__ = ["TelegramNotifier"]
