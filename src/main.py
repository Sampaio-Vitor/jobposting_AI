from langdetect import detect, LangDetectException
from src import database, scraper, analyzer, notifier
from src.logger import log


def _is_english(text: str) -> bool:
    """Check if text is in English using langdetect."""
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False


def run():
    log.info("=== AI/ML Job Tracker ===")

    # 1. Init database
    database.init_db()

    # 2. Scrape jobs
    jobs = scraper.fetch_jobs()
    new_count = database.upsert_jobs(jobs)
    log.info(f"Scraped {len(jobs)} jobs, {new_count} new")

    # 3. Filter: only English job postings go to LLM
    unanalyzed = database.get_unanalyzed()
    if unanalyzed:
        english_jobs = []
        skipped = 0
        for job in unanalyzed:
            text = f"{job['title']} {job['description']}"
            if _is_english(text):
                english_jobs.append(job)
            else:
                skipped += 1
                # Mark non-English jobs as analyzed but not relevant
                database.save_analysis(job["id"], {
                    "is_relevant": False, "is_remote": False, "is_international": False,
                    "role_category": "N/A", "seniority": "N/A",
                    "summary": "Skipped: not in English", "salary_range": None,
                })

        log.info(f"{len(unanalyzed)} unanalyzed jobs: {len(english_jobs)} English, {skipped} skipped (not English)")

        if english_jobs:
            log.info(f"Analyzing {len(english_jobs)} jobs with Gemini...")
            results = analyzer.analyze_jobs(english_jobs)
            for job_id, analysis in results:
                database.save_analysis(job_id, analysis)
            log.info(f"Analyzed {len(results)} jobs")
    else:
        log.info("No new jobs to analyze")

    # 4. Send matching jobs to Telegram
    matches = database.get_unnotified_matches()
    if matches:
        log.info(f"Found {len(matches)} matching jobs (relevant + remote + international)")
        notifier.send_daily_digest(matches)
        database.mark_notified([j["id"] for j in matches])
    else:
        log.info("No new matching jobs today.")

    log.info("=== Done ===")


if __name__ == "__main__":
    run()
