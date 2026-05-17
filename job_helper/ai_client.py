from __future__ import annotations

import json
from openai import OpenAI

from job_helper.config import Settings
from job_helper.prompts import SYSTEM_PROMPT, build_user_prompt
from job_helper.schemas import JobFitAnalysis


def analyze_job_with_openai(job_description: str, settings: Settings) -> JobFitAnalysis:
    client = OpenAI(api_key=settings.openai_api_key)

    schema = JobFitAnalysis.model_json_schema()

    response = client.responses.create(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        input=build_user_prompt(job_description),
        text={
            "format": {
                "type": "json_schema",
                "name": "job_fit_analysis",
                "schema": schema,
                "strict": True,
            }
        },
    )

    raw = response.output_text
    data = json.loads(raw)
    return JobFitAnalysis.model_validate(data)
