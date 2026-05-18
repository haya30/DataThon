from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class StartInterviewResponse(BaseModel):
    message: str
    session_id: str
    cv_text_preview: str
    first_question: Optional[Dict[str, Any]]
    total_questions: int


class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str


class SubmitAnswerResponse(BaseModel):
    is_completed: bool
    type: Optional[str] = None
    question: Optional[Dict[str, Any]] = None
    current_index: Optional[int] = None
    answers: List[Dict[str, Any]]
    message: Optional[str] = None