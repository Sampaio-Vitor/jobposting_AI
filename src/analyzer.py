import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google import genai
from src import config
from src.models import JobAnalysis
from src.logger import log

MODEL = "gemini-3-flash-preview"
MAX_WORKERS = 10
MAX_RETRIES = 3

PROMPT_TEMPLATE = """You are a strict job classifier. Analyze this job posting.

CRITICAL: is_relevant must be TRUE **only** if the job's PRIMARY function involves one of these:
- Machine Learning / Deep Learning (building, training, deploying models)
- AI Engineering (building AI systems, LLM applications, AI agents)
- MLOps (ML infrastructure, model serving, ML pipelines)
- NLP / Computer Vision / Reinforcement Learning
- Data Science with heavy ML focus (not just SQL/dashboards/BI)

is_relevant must be FALSE for:
- Generic software engineering, even if "AI tools" are mentioned
- Project managers, product managers, sales, HR, finance, marketing
- Data analysts, BI analysts, database administrators
- Any role where AI/ML is NOT the core job function
- Roles that just "use" AI tools but don't build them
- Data annotation, labeling, RLHF, or "AI training" roles (mechanical turk work)
- Roles focused on rating, reviewing, evaluating, or benchmarking AI/LLM outputs
- Content moderation for AI systems
- "Evaluation" or "assessment" roles disguised as ML Engineer/Data Scientist — if the PRIMARY task is writing evaluation suites, assessing AI-generated solutions, or creating benchmarks for AI models (not building the models themselves), mark as NOT relevant
- Project-based or contract roles at staffing agencies (e.g. Keystone, Nexus, Appen, Scale AI, Outlier) where the work is evaluating/scoring model outputs

is_international: TRUE only if the job explicitly says it accepts candidates from outside Brazil, or is listed as remote/worldwide/global/anywhere

Job posting:
Title: {title}
Company: {company}
Location: {location}

Description:
{description}"""


_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _analyze_one(job: dict) -> tuple[str, dict | None, str | None]:
    """Analyze a single job with retries on 503. Returns (job_id, analysis_dict, error_msg)."""
    client = _get_client()
    prompt = PROMPT_TEMPLATE.format(
        title=job["title"],
        company=job["company"],
        location=job["location"],
        description=job["description"][:3000],
    )
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": JobAnalysis,
                },
            )
            result: JobAnalysis = response.parsed
            return (job["id"], result.model_dump(), None)
        except Exception as e:
            if "503" in str(e) and attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)
                continue
            return (job["id"], None, str(e))


def analyze_jobs(jobs: list[dict]) -> list[tuple[str, dict]]:
    """Analyze multiple jobs in parallel. Returns list of (job_id, analysis_dict) tuples."""
    log.info(f"Analyzing {len(jobs)} jobs with {MAX_WORKERS} parallel workers...")
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_analyze_one, job): job for job in jobs}

        for i, future in enumerate(as_completed(futures), 1):
            job = futures[future]
            job_id, analysis, error = future.result()

            if error:
                log.error(f"[{i}/{len(jobs)}] Failed: {job['title']} @ {job['company']} — {error}")
            else:
                status = "MATCH" if (analysis["is_relevant"] and analysis["is_international"]) else "skip"
                log.info(f"[{i}/{len(jobs)}] {status} | {job['title']} @ {job['company']} | intl={analysis['is_international']} relevant={analysis['is_relevant']}")
                results.append((job_id, analysis))

    return results
