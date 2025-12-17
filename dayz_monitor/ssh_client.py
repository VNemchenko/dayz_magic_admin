from __future__ import annotations

import io
import logging
import posixpath
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Optional

import paramiko

from .config import Settings

LOGGER = logging.getLogger(__name__)


@dataclass
class LogLocation:
    directory: str
    filename: str

    @property
    def full_path(self) -> str:
        return posixpath.join(self.directory, self.filename)


class SshLogClient:
    """Provides read-only access to DayZ log files over SSH/SFTP."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None

    def __enter__(self) -> "SshLogClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def connect(self) -> None:
        if self._client:
            return
        LOGGER.debug("Establishing SSH connection to %s:%s", self._settings.ssh_host, self._settings.ssh_port)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        pkey = None
        if self._settings.ssh_private_key:
            pkey = paramiko.RSAKey.from_private_key(io.StringIO(self._settings.ssh_private_key))

        client.connect(
            hostname=self._settings.ssh_host,
            port=self._settings.ssh_port,
            username=self._settings.ssh_username,
            password=self._settings.ssh_password,
            pkey=pkey,
            look_for_keys=False,
        )
        self._client = client
        self._sftp = client.open_sftp()
        LOGGER.info("SSH connection established")

    def close(self) -> None:
        if self._sftp:
            self._sftp.close()
            self._sftp = None
        if self._client:
            self._client.close()
            self._client = None
        LOGGER.info("SSH connection closed")

    def find_todays_log(self, target_date: Optional[date] = None) -> Optional[LogLocation]:
        if not self._sftp:
            raise RuntimeError("SFTP client is not connected")

        target = target_date or date.today()
        prefix = f"DayZServer_{target.isoformat()}_"
        LOGGER.debug("Looking for log files with prefix %s in %s", prefix, self._settings.logs_path)
        try:
            entries = self._sftp.listdir(self._settings.logs_path)
        except FileNotFoundError:
            LOGGER.error("Logs directory %s not found", self._settings.logs_path)
            return None

        matching = sorted(name for name in entries if name.startswith(prefix) and name.endswith(".ADM"))
        if not matching:
            LOGGER.warning("No DayZ log files found for %s", target)
            return None

        latest = matching[-1]
        LOGGER.info("Selected log file %s", latest)
        return LogLocation(directory=self._settings.logs_path, filename=latest)

    def read_lines(self, location: LogLocation) -> List[str]:
        if not self._sftp:
            raise RuntimeError("SFTP client is not connected")
        LOGGER.debug("Reading log file %s", location.full_path)
        with self._sftp.open(location.full_path, "r") as handle:
            raw = handle.read()
            text = raw.decode("utf-8", errors="ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)
            return text.splitlines()


__all__ = ["SshLogClient", "LogLocation"]
