from jobspy import scrape_jobs
from src.logger import log


SEARCH_TERM = (
    '("machine learning" OR "ML engineer" OR "AI engineer" OR "artificial intelligence"'
    ' OR "MLOps" OR "LLM" OR "NLP"'
    ' OR "data scientist")'
)


def fetch_jobs() -> list[dict]:
    """Scrape AI/ML jobs from LinkedIn Brazil (last 24h)."""
    log.info("Scraping LinkedIn for AI/ML jobs...")

    df = scrape_jobs(
        site_name=["linkedin"],
        search_term=SEARCH_TERM,
        location="Brazil",
        results_wanted=100,
        hours_old=24,
        linkedin_fetch_description=True,
    )

    log.info(f"Found {len(df)} jobs from LinkedIn")

    jobs = []
    for _, row in df.iterrows():
        job_id = str(row.get("id", ""))
        if not job_id:
            continue

        jobs.append({
            "id": job_id,
            "title": str(row.get("title", "")),
            "company": str(row.get("company", "")),
            "location": str(row.get("location", "")),
            "link": str(row.get("job_url", "")),
            "description": str(row.get("description", "")),
            "date_posted": str(row.get("date_posted", "")),
            "salary_min": row.get("min_amount"),
            "salary_max": row.get("max_amount"),
            "salary_currency": row.get("currency"),
        })

    return jobs
