import asyncio
from datetime import date
from telegram import Bot
from telegram.constants import ParseMode
from src import config
from src.logger import log

MAX_MESSAGE_LENGTH = 4096


def _format_salary(job: dict) -> str | None:
    """Build salary line. Prefers scraper data over Gemini extraction."""
    sal_min = job.get("salary_min")
    sal_max = job.get("salary_max")
    currency = job.get("salary_currency") or "USD"

    if sal_min or sal_max:
        if sal_min and sal_max:
            return f"{currency} {sal_min:,.0f} – {sal_max:,.0f}"
        return f"{currency} {(sal_min or sal_max):,.0f}"

    gemini_range = job.get("salary_range")
    if gemini_range:
        return gemini_range

    return None


def _format_digest(jobs: list[dict]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    header = f"<b>AI/ML Jobs — {today}</b>\n\nFound <b>{len(jobs)}</b> international remote positions:\n"

    entries = []
    for i, job in enumerate(jobs, 1):
        title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        seniority = job.get("seniority", "")
        summary = job.get("summary", "")
        link = job.get("link", "")
        category = job.get("role_category", "")
        salary = _format_salary(job)

        entry = (
            f"\n<b>{i}. {title}</b> @ {company}"
            f"\n   {category} — {seniority}"
        )
        if salary:
            entry += f"\n   {salary}"
        entry += (
            f"\n   <i>{summary}</i>"
            f'\n   <a href="{link}">View on LinkedIn</a>'
        )
        entries.append(entry)

    return header + "\n".join(entries)


def _split_message(text: str) -> list[str]:
    """Split message into chunks that fit Telegram's limit."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        return [text]

    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > MAX_MESSAGE_LENGTH:
            chunks.append(current)
            current = line
        else:
            current += "\n" + line if current else line
    if current:
        chunks.append(current)
    return chunks


async def _send(messages: list[str]):
    bot = Bot(token=config.TELEGRAM_TOKEN)
    for msg in messages:
        await bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=msg,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )


def send_daily_digest(jobs: list[dict]):
    """Send the daily job digest to Telegram."""
    log.info(f"Sending {len(jobs)} jobs to Telegram...")
    text = _format_digest(jobs)
    chunks = _split_message(text)
    asyncio.run(_send(chunks))
    log.info("Telegram notification sent!")
