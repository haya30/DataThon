import uuid


sessions = {}


def create_session(cv_text: str, questions: list, interview_engine):
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "cv_text": cv_text,
        "questions": questions,
        "engine": interview_engine
    }

    return session_id


def get_session(session_id: str):
    return sessions.get(session_id)


def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]