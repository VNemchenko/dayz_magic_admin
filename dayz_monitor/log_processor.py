from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List

from .config import Settings

LOGGER = logging.getLogger(__name__)
_TIME_PATTERN = re.compile(r"^(?P<time>\d{2}:\d{2}:\d{2})")


@dataclass
class LogSlice:
    since: datetime
    until: datetime
    lines: List[str]


def parse_line_time(line: str, reference_date: datetime) -> datetime | None:
    match = _TIME_PATTERN.match(line)
    if not match:
        return None
    time_part = match.group("time")
    try:
        parsed = datetime.strptime(time_part, "%H:%M:%S")
    except ValueError:
        return None
    return reference_date.replace(hour=parsed.hour, minute=parsed.minute, second=parsed.second, microsecond=0)


def extract_recent_lines(settings: Settings, lines: Iterable[str], now: datetime) -> LogSlice | None:
    target_since = (now - timedelta(minutes=1)).replace(second=0, microsecond=0)
    target_until = target_since + timedelta(minutes=1)
    LOGGER.debug("Collecting log lines between %s and %s", target_since, target_until)

    collected: List[str] = []
    for raw_line in lines:
        if settings.is_ignored(raw_line):
            continue
        timestamp = parse_line_time(raw_line, reference_date=target_since)
        if not timestamp:
            continue
        if target_since <= timestamp < target_until:
            collected.append(raw_line)

    if not collected:
        LOGGER.info("No log lines found for target minute")
        return None

    LOGGER.info("Collected %s log lines for analysis", len(collected))
    return LogSlice(since=target_since, until=target_until, lines=collected)


__all__ = ["LogSlice", "extract_recent_lines"]
