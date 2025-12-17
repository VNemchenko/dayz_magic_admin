from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from .config import Settings
from .log_processor import extract_recent_lines
from .openrouter_client import LogAnalyzer
from .ssh_client import SshLogClient
from .telegram_client import TelegramNotifier

LOGGER = logging.getLogger(__name__)


def run_once(settings: Settings, analyzer: LogAnalyzer, notifier: TelegramNotifier) -> None:
    now = datetime.now(tz=settings.timezone)
    LOGGER.debug("Starting log cycle at %s", now)
    with SshLogClient(settings) as ssh:
        location = ssh.find_todays_log(target_date=now.date())
        if not location:
            return

        lines = ssh.read_lines(location)
        log_slice = extract_recent_lines(settings, lines, now=now)
        if not log_slice:
            return

    analysis = analyzer.analyze(log_slice.lines)
    message = (
        f"DayZ logs {log_slice.since:%Y-%m-%d %H:%M} - {log_slice.until:%H:%M}\n"
        f"{analysis}"
    )
    notifier.send(message, parse_mode="Markdown")


def run_service(settings: Settings) -> None:
    settings.validate()
    analyzer = LogAnalyzer(settings)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)

    LOGGER.info("Starting DayZ log monitoring service")
    while True:
        try:
            run_once(settings, analyzer, notifier)
        except Exception:  # noqa: BLE001
            LOGGER.exception("Error while processing log cycle")
        time.sleep(settings.poll_interval_seconds)


__all__ = ["run_service", "run_once"]
