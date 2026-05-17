from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, ConfigDict, Field


class JobFitAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str = Field(description="Company name")
    title: str = Field(description="Job title")
    location: str = Field(description="Job location or remote/hybrid status if available")
    experience_level: str = Field(description="Entry, New Grad, Internship, Mid-level, Senior, Staff, Unknown")
    technical_fit_score: int = Field(ge=0, le=100)
    hiring_competitiveness_score: int = Field(ge=0, le=100)
    apply_priority: Literal["High", "Medium", "Low"]
    sponsorship_risk: Literal["Low", "Medium", "High", "Unknown"]
    ats_keyword_match: int = Field(ge=0, le=100)
    best_fit_reasons: List[str]
    major_gaps: List[str]
    required_skills_found: List[str]
    missing_keywords: List[str]
    recommended_resume_keywords: List[str]
    recommended_resume_strategy: str
    suggested_cover_letter_angle: str
    next_action: str
    short_reasoning: str