from __future__ import annotations

import logging
import sys

from dotenv import load_dotenv

from dayz_monitor.config import Settings
from dayz_monitor.service import run_service


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


def main() -> None:
    load_dotenv()
    configure_logging()
    settings = Settings.from_env()
    run_service(settings)


if __name__ == "__main__":
    main()
