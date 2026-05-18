class ReportGenerator:
    """
    Converts evaluation results into a clean HR report.
    """

    def generate_report(self, candidate_name: str, job_role: str, evaluation: dict) -> dict:
        fit_score = evaluation.get("fit_score")
        knowledge_score = evaluation.get("knowledge_score")
        communication_score = evaluation.get("communication_score")
        recommendation = evaluation.get("recommendation")

        summary = self._build_summary(
            candidate_name=candidate_name,
            job_role=job_role,
            fit_score=fit_score,
            recommendation=recommendation
        )

        return {
            "candidate_name": candidate_name,
            "job_role": job_role,
            "summary": summary,
            "scores": {
                "fit_score": fit_score,
                "knowledge_score": knowledge_score,
                "communication_score": communication_score
            },
            "recommendation": recommendation,
            "dimension_breakdown": evaluation.get("dimensions", {}),
            "strengths": evaluation.get("strengths", []),
            "weaknesses": evaluation.get("weaknesses", []),
            "risks": evaluation.get("risks", []),
            "hr_decision_note": self._build_hr_note(recommendation)
        }

    def _build_summary(self, candidate_name: str, job_role: str, fit_score: int, recommendation: str) -> str:
        return (
            f"{candidate_name} was evaluated for the {job_role} role. "
            f"The candidate received a Fit Score of {fit_score}/100 with a final recommendation of "
            f"'{recommendation}'. The evaluation is based on interview answers and the Data Analyst rubric."
        )

    def _build_hr_note(self, recommendation: str) -> str:
        if recommendation == "Recommend":
            return "Candidate appears suitable for the role and can move to the next hiring stage."
        elif recommendation == "Maybe":
            return "Candidate shows potential, but further assessment is recommended before making a final decision."
        elif recommendation == "Conditional":
            return "Candidate requires a follow-up interview to validate gaps or unclear evidence."
        else:
            return "Candidate is not recommended for this role based on the current evaluation."