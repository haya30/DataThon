from app.services.cv_parser import CVParser
from app.services.question_generator import QuestionGenerator
from app.services.interview_engine import InterviewEngine
from app.services.evaluator import Evaluator
from app.services.report_generator import ReportGenerator


class NukhbaAgent:
    """
    Main orchestrator for NUKHBA AI Agent.

    This class connects:
    - CV parsing
    - Question generation
    - Interview flow
    - Evaluation
    - HR report generation

    It gives the API layer one simple interface to use.
    """

    def __init__(self):
        self.cv_parser = CVParser()
        self.question_generator = QuestionGenerator()
        self.evaluator = Evaluator()
        self.report_generator = ReportGenerator()

    async def generate_interview_questions(self, cv_text: str, language: str = "English") -> dict:
        """
        Parse CV, then generate interview questions.
        """

        # ✅ 1. Parse CV
        parsed_cv = await self.cv_parser.parse(cv_text)

        # ✅ 2. enrich input للـAI
        enriched_cv_text = f"""
Raw CV:
{cv_text}

Parsed CV:
{parsed_cv}
"""

        # ✅ 3. Generate questions باستخدام parsed_cv
        result = await self.question_generator.generate_questions(
            cv_text=enriched_cv_text,
            language=language,
            parsed_cv=parsed_cv
        )

        return {
            "parsed_cv": parsed_cv,
            "questions": result["questions"]
        }

    def create_interview_session(self, questions: list) -> InterviewEngine:
        """
        Create an interview session using generated questions.

        Note:
        The API layer should store this session using a session_id.
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
        Parse CV, evaluate answers, and generate HR report.
        """

        # ✅ 1. Parse CV
        parsed_cv = await self.cv_parser.parse(cv_text)

        enriched_cv_text = f"""
Raw CV:
{cv_text}

Parsed CV:
{parsed_cv}
"""

        # ✅ 2. Evaluate
        evaluation = await self.evaluator.evaluate(
            answers=answers,
            cv_text=enriched_cv_text,
            job_description=job_description
        )

        # ✅ 3. Generate report
        report = self.report_generator.generate_report(
            candidate_name=candidate_name,
            job_role=job_role,
            evaluation=evaluation
        )

        return {
            "parsed_cv": parsed_cv,
            "evaluation": evaluation,
            "report": report
        }