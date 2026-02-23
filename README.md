# AI/ML Job Tracker

Automated pipeline that scrapes AI/ML job postings from LinkedIn, classifies them with Gemini, and sends matching remote+international opportunities to Telegram.

## How it works

1. **Scrape** — Fetches AI/ML jobs from LinkedIn Brazil via [python-jobspy](https://github.com/Bunsly/JobSpy)
2. **Filter** — Skips non-English postings (langdetect)
3. **Analyze** — Classifies each job with Gemini 2.5 Flash-Lite (remote? international? relevant?)
4. **Notify** — Sends matching jobs to Telegram

## Setup

```bash
cp .env.example .env
# Fill in your keys: GEMINI_API_KEY, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
```

## Run

```bash
docker compose up --build
```

## Stack

- Python 3.12
- Google Gemini (structured output)
- SQLite (WAL mode)
- Telegram Bot API
- Docker
