from app.services.question_generator import QuestionGenerator
from app.services.interview_engine import InterviewEngine
from app.services.evaluator import Evaluator
from app.services.report_generator import ReportGenerator


class NukhbaAgent:
    """
    Main orchestrator for NUKHBA AI Agent.

    This class connects:
    - Question generation
    - Interview flow
    - Evaluation
    - HR report generation

    It gives the API layer one simple interface to use.
    """

    def __init__(self):
        self.question_generator = QuestionGenerator()
        self.evaluator = Evaluator()
        self.report_generator = ReportGenerator()

    async def generate_interview_questions(self, cv_text: str, language: str = "English") -> dict:
        """
        Generate Data Analyst interview questions from CV.
        """
        return await self.question_generator.generate_questions(
            cv_text=cv_text,
            language=language
        )

    def create_interview_session(self, questions: list) -> InterviewEngine:
        """
        Create an interview session using generated questions.

        Note:
        The API layer should store this session in memory/database
        using a session_id.
        """
        return InterviewEngine(questions)

    async def evaluate_candidate(
        self,
        candidate_name: str,
        job_role: str,
        answers: list,
        cv_text: str = "",
        job_description: str = ""
    ) -> dict:
        """
        Evaluate candidate answers and generate a full HR report.
        """

        evaluation = await self.evaluator.evaluate(
            answers=answers,
            cv_text=cv_text,
            job_description=job_description
        )

        report = self.report_generator.generate_report(
            candidate_name=candidate_name,
            job_role=job_role,
            evaluation=evaluation
        )

        return {
            "evaluation": evaluation,
            "report": report
        }