from pydantic import BaseModel
from typing import Any, Dict


class FinalEvaluationRequest(BaseModel):
    session_id: str
    candidate_name: str
    job_role: str = "Data Analyst"
    job_description: str = ""


class FinalEvaluationResponse(BaseModel):
    evaluation: Dict[str, Any]
    report: Dict[str, Any]