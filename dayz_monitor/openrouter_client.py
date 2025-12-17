from __future__ import annotations

import logging
from typing import Iterable

from openai import OpenAI

from .config import Settings

LOGGER = logging.getLogger(__name__)


class LogAnalyzer:
    """Uses an OpenAI-compatible endpoint on OpenRouter to analyze log content."""

    def __init__(self, settings: Settings):
        self._client = OpenAI(api_key=settings.openrouter_api_key, base_url="https://openrouter.ai/api/v1")
        self._model = settings.openrouter_model

    def analyze(self, logs: Iterable[str]) -> str:
        log_list = list(logs)
        prompt_lines = [
            "You are monitoring a DayZ game server.",
            "Summarize the following log lines from the last minute.",
            "Highlight potential issues, kicks/bans, or anomalies in a concise bullet list.",
            "Log lines:",
        ]
        prompt_lines.extend(log_list)
        prompt = "\n".join(prompt_lines)

        LOGGER.debug("Sending %s log lines to OpenRouter for analysis", len(log_list))
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes DayZ server events."},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        LOGGER.info("Received response from OpenRouter")
        return content or "(empty response)"


__all__ = ["LogAnalyzer"]
