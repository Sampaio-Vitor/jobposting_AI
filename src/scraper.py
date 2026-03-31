from jobspy import scrape_jobs
from src.logger import log


SEARCH_TERM = "machine learning"

# JobSpy's LinkedIn scraper paginates until `start < 1000`, so 1000 is the
# effective "fetch as many as available" ceiling for a single search.
RESULTS_WANTED = 1000


def fetch_jobs() -> list[dict]:
    """Scrape LinkedIn jobs for the current search term in Brazil (last 24h)."""
    log.info(f"Scraping LinkedIn for jobs matching: {SEARCH_TERM}")

    df = scrape_jobs(
        site_name=["linkedin"],
        search_term=SEARCH_TERM,
        location="Brazil",
        results_wanted=RESULTS_WANTED,
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
