from fastapi import APIRouter, HTTPException

from app.schemas.evaluation import FinalEvaluationRequest, FinalEvaluationResponse
from app.storage.memory_store import get_session
from app.services.agent_orchestrator import NukhbaAgent


router = APIRouter(
    prefix="/api/evaluation",
    tags=["Evaluation"]
)

agent = NukhbaAgent()


@router.post("/final", response_model=FinalEvaluationResponse)
async def final_evaluation(request: FinalEvaluationRequest):

    session = get_session(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    engine = session["engine"]

    answers = engine.answers
    cv_text = session["cv_text"]

    result = await agent.evaluate_candidate(
        candidate_name=request.candidate_name,
        job_role=request.job_role,
        answers=answers,
        cv_text=cv_text,
        job_description=request.job_description
    )

    return result