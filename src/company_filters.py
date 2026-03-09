import re


BLOCKED_COMPANIES_RE = re.compile(
    r"(bluelight|fullstack|get\W*offers|lumenalta|oowlish|georgiatek\W*systems|tata|agileengine|jobgether)",
    re.IGNORECASE,
)


def is_blocked_company(company: str) -> bool:
    return bool(BLOCKED_COMPANIES_RE.search(company or ""))
