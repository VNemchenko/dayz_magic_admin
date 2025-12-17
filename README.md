# dayz_magic_admin

## DayZ log monitoring service

This repository contains a Python service that connects to a remote DayZ server via SSH, gathers log lines from the latest `DayZServer_<date>_*.ADM` file, summarizes the previous minute of activity using an OpenRouter-hosted LLM, and forwards the summary to a Telegram chat.

### Configuration

Set the following environment variables (a `.env` file is supported):

| Variable | Description |
| --- | --- |
| `SSH_HOST` | SSH hostname of the DayZ server. |
| `SSH_PORT` | SSH port (default: `22`). |
| `SSH_USERNAME` | SSH username. |
| `SSH_PASSWORD` | SSH password (use `SSH_PRIVATE_KEY` instead for key auth). |
| `SSH_PRIVATE_KEY` | Private key contents for SSH authentication. |
| `DAYZ_LOGS_PATH` | Remote directory containing DayZ log files. |
| `POLL_INTERVAL_SECONDS` | Interval between checks (default: `60`). |
| `LOG_IGNORE_FILTERS` | Comma-separated substrings to ignore in logs. |
| `DAYZ_TIMEZONE` | IANA timezone for timestamp parsing (default: UTC). |
| `OPENROUTER_API_KEY` | API key for https://openrouter.ai. |
| `OPENROUTER_MODEL` | Model ID to use (default: `openrouter/auto`). |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for sending messages. |
| `TELEGRAM_CHAT_ID` | Telegram chat ID that receives summaries. |

### Running locally

```bash
pip install -r requirements.txt
python main.py
```

The service will run continuously, checking the log file once per minute and delivering summaries to the configured Telegram chat.

### Running with Docker Compose

1. Create a `.env` file with the configuration variables from the table above.
2. Build and start the container:

```bash
docker compose up --build
```

The service will start with the minimal `python:3.12-slim` base image and restart automatically unless stopped.
