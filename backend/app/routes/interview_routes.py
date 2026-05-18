from fastapi import APIRouter, UploadFile, File, HTTPException

from app.utils.pdf_extractor import extract_text_from_pdf
from app.services.agent_orchestrator import NukhbaAgent
from app.storage.memory_store import create_session, get_session
from app.schemas.interview import StartInterviewResponse, SubmitAnswerRequest, SubmitAnswerResponse


router = APIRouter(prefix="/api/interview", tags=["Interview"])

agent = NukhbaAgent()


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(cv_file: UploadFile = File(...)):
    if cv_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    cv_text = extract_text_from_pdf(cv_file)

    if not cv_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    result = await agent.generate_interview_questions(cv_text)
    questions = result.get("questions", result)

    engine = agent.create_interview_session(questions)
    session_id = create_session(cv_text, questions, engine)

    first_question = engine.get_current_question()

    return {
        "message": "Interview started successfully",
        "session_id": session_id,
        "cv_text_preview": cv_text[:500],
        "first_question": first_question,
        "total_questions": len(questions)
    }


@router.post("/answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    session = get_session(request.session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    engine = session["engine"]
    result = engine.submit_answer(request.answer)

    return result