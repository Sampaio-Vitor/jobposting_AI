from pydantic import BaseModel, Field
from typing import Optional


class JobAnalysis(BaseModel):
    """Structured output schema for Gemini analysis."""

    is_relevant: bool = Field(description="Is this an AI/ML role? (ML Engineer, AI Engineer, MLOps, LLM, NLP, CV, Deep Learning, GenAI)")
    is_international: bool = Field(description="Can someone outside Brazil apply? Is it open to international candidates?")
    role_category: str = Field(description="One of: ML Engineer, AI Engineer, MLOps, LLM Engineer, NLP Engineer, CV Engineer, Data Scientist, Other")
    seniority: str = Field(description="One of: Junior, Mid, Senior, Lead")
    summary: str = Field(description="2-3 line summary of the role and key requirements")
    salary_range: Optional[str] = Field(default=None, description="Salary range if mentioned in the posting, else null")
