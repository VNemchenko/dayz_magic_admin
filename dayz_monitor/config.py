from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import timezone
from typing import Iterable, List, Optional
from zoneinfo import ZoneInfo


@dataclass
class Settings:
    """Runtime configuration derived from environment variables."""

    ssh_host: str
    ssh_username: str
    ssh_password: Optional[str] = None
    ssh_port: int = 22
    ssh_private_key: Optional[str] = None
    logs_path: str = "."
    poll_interval_seconds: int = 60
    ignore_filters: List[str] = field(default_factory=list)
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/auto"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    timezone: timezone = timezone.utc

    @classmethod
    def from_env(cls) -> "Settings":
        def split_list(value: Optional[str]) -> List[str]:
            if not value:
                return []
            return [item.strip() for item in value.split(",") if item.strip()]

        timezone_override = os.getenv("DAYZ_TIMEZONE")
        tz = timezone.utc
        if timezone_override:
            try:
                tz = ZoneInfo(timezone_override)
            except Exception as exc:  # noqa: BLE001
                raise ValueError(f"Invalid DAYZ_TIMEZONE value: {timezone_override}") from exc

        return cls(
            ssh_host=os.environ["SSH_HOST"],
            ssh_username=os.environ["SSH_USERNAME"],
            ssh_password=os.getenv("SSH_PASSWORD"),
            ssh_port=int(os.getenv("SSH_PORT", "22")),
            ssh_private_key=os.getenv("SSH_PRIVATE_KEY"),
            logs_path=os.getenv("DAYZ_LOGS_PATH", "."),
            poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "60")),
            ignore_filters=split_list(os.getenv("LOG_IGNORE_FILTERS")),
            openrouter_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            openrouter_model=os.getenv("OPENROUTER_MODEL", "openrouter/auto"),
            telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
            timezone=tz,
        )

    def validate(self) -> None:
        missing: List[str] = []
        if not self.ssh_host:
            missing.append("SSH_HOST")
        if not self.ssh_username:
            missing.append("SSH_USERNAME")
        if not (self.ssh_password or self.ssh_private_key):
            missing.append("SSH_PASSWORD or SSH_PRIVATE_KEY")
        if not self.openrouter_api_key:
            missing.append("OPENROUTER_API_KEY")
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.telegram_chat_id:
            missing.append("TELEGRAM_CHAT_ID")
        if missing:
            raise ValueError(f"Missing required configuration values: {', '.join(missing)}")

    def is_ignored(self, line: str) -> bool:
        for pattern in self.ignore_filters:
            if pattern in line:
                return True
        return False


__all__ = ["Settings"]
