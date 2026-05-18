import json
from collections import defaultdict

from app.config import settings
from app.llm.openrouter_provider import OpenRouterProvider
from app.services.scoring import calculate_scores, get_recommendation


class Evaluator:
    """
    Evaluates candidate answers using:
    - LLM if USE_LLM=true
    - Smart rule-based fallback if USE_LLM=false or LLM fails
    """

    def __init__(self):
        self.llm = OpenRouterProvider()

    async def evaluate(self, answers: list, cv_text: str = "", job_description: str = "") -> dict:
        if settings.use_llm:
            try:
                return await self._evaluate_with_llm(answers, cv_text, job_description)
            except Exception:
                print("⚠️ LLM failed, using smart rule-based fallback")
                return self._evaluate_rule_based(answers)

        return self._evaluate_rule_based(answers)

    async def _evaluate_with_llm(self, answers: list, cv_text: str, job_description: str) -> dict:
        prompt = f"""
You are NUKHBA, an AI HR evaluation agent.

Evaluate this Data Analyst candidate using the rubric below.

Rubric dimensions:
D1 Technical Skills & Tools
D2 Analytical & Statistical Thinking
D3 Business Acumen & Insight Communication
D4 Experience & Project Ownership
D5 Role Fit & Soft Signals

Level mapping:
Level 5 = Expert
Level 4 = Strong
Level 3 = Adequate
Level 2 = Below Bar
Level 1 = Insufficient

Rules:
- Be evidence-based.
- Do not guess if evidence is missing.
- Use Low confidence when evidence is weak.
- Return ONLY valid JSON.
- Do not add markdown or explanation outside JSON.

JSON format:
{{
  "dimensions": {{
    "D1": {{"level": 4, "confidence": "High", "evidence": ["..."]}},
    "D2": {{"level": 3, "confidence": "Medium", "evidence": ["..."]}},
    "D3": {{"level": 3, "confidence": "Medium", "evidence": ["..."]}},
    "D4": {{"level": 3, "confidence": "Medium", "evidence": ["..."]}},
    "D5": {{"level": 3, "confidence": "Medium", "evidence": ["..."]}}
  }},
  "strengths": ["..."],
  "weaknesses": ["..."],
  "risks": ["..."]
}}

Candidate CV:
{cv_text}

Job Description:
{job_description}

Interview Answers:
{json.dumps(answers, ensure_ascii=False)}
"""

        response = await self.llm.chat([
            {
                "role": "system",
                "content": "You are a strict, fair, evidence-based HR evaluation agent."
            },
            {
                "role": "user",
                "content": prompt
            }
        ])

        llm_result = json.loads(response)

        levels = {
            dim: data["level"]
            for dim, data in llm_result["dimensions"].items()
        }

        for d in ["D1", "D2", "D3", "D4", "D5"]:
            levels.setdefault(d, 3)

        scores = calculate_scores(levels)
        recommendation = get_recommendation(scores["fit_score"])

        return {
            **llm_result,
            "dimension_levels": levels,
            **scores,
            "recommendation": recommendation
        }

    def _evaluate_rule_based(self, answers: list) -> dict:
        grouped_answers = defaultdict(list)

        for item in answers:
            dimension_key = item["dimension"].split()[0]
            grouped_answers[dimension_key].append(item)

        final_levels = {}
        dimensions = {}

        for dim in ["D1", "D2", "D3", "D4", "D5"]:
            items = grouped_answers.get(dim, [])
            level = self._score_dimension(dim, items)
            final_levels[dim] = level

            dimensions[dim] = {
                "level": level,
                "confidence": self._confidence_for_dimension(items),
                "evidence": self._build_evidence(dim, items, level)
            }

        scores = calculate_scores(final_levels)
        recommendation = get_recommendation(scores["fit_score"])

        return {
            "dimensions": dimensions,
            "dimension_levels": final_levels,
            "strengths": self._build_strengths(final_levels, dimensions),
            "weaknesses": self._build_weaknesses(final_levels, dimensions),
            "risks": self._build_risks(final_levels, dimensions),
            **scores,
            "recommendation": recommendation
        }

    def _score_dimension(self, dim: str, items: list) -> int:
        if not items:
            return 3

        answers_text = " ".join(item.get("answer", "") for item in items).lower()
        total_words = len(answers_text.split())

        score = 3

        if total_words < 15:
            score = 2
        elif total_words >= 35:
            score = 4
        elif total_words >= 70:
            score = 5

        keyword_bonus = {
            "D1": ["sql", "join", "group", "distinct", "excel", "power bi", "python", "pandas"],
            "D2": ["segment", "root cause", "trend", "compare", "conversion", "metric", "analyze"],
            "D3": ["stakeholder", "business", "impact", "recommend", "explain", "decision"],
            "D4": ["owned", "led", "built", "delivered", "project", "requirements"],
            "D5": ["clear", "structured", "example", "specific", "learned"]
        }

        hits = sum(1 for keyword in keyword_bonus.get(dim, []) if keyword in answers_text)

        if hits >= 3 and score < 4:
            score = 4
        elif hits == 0 and score > 3:
            score = 3

        return min(score, 5)

    def _confidence_for_dimension(self, items: list) -> str:
        if not items:
            return "Low"

        total_words = sum(len(item.get("answer", "").split()) for item in items)

        if total_words >= 40:
            return "Medium"
        if total_words >= 20:
            return "Medium"

        return "Low"

    def _build_evidence(self, dim: str, items: list, level: int) -> list:
        if not items:
            return ["No direct interview evidence was collected for this dimension."]

        answers_text = " ".join(item.get("answer", "") for item in items).lower()

        if dim == "D1":
            if any(k in answers_text for k in ["sql", "join", "group", "distinct"]):
                return ["Candidate mentioned SQL logic such as joins, grouping, or counting distinct users."]
            if any(k in answers_text for k in ["excel", "power bi", "python", "pandas"]):
                return ["Candidate referenced relevant data analysis tools such as Excel, Power BI, Python, or Pandas."]
            return ["Candidate provided limited technical detail in the answers."]

        if dim == "D2":
            if any(k in answers_text for k in ["segment", "root cause", "trend", "compare"]):
                return ["Candidate described analytical steps such as segmentation, comparison, or root-cause investigation."]
            return ["Candidate showed basic analytical reasoning, but evidence is limited."]

        if dim == "D3":
            if any(k in answers_text for k in ["stakeholder", "business", "impact", "recommend", "decision"]):
                return ["Candidate connected analysis to stakeholders, business impact, or decision-making."]
            return ["Candidate communication evidence is present but not strongly linked to business impact."]

        if dim == "D4":
            if any(k in answers_text for k in ["owned", "led", "built", "delivered", "project"]):
                return ["Candidate described participation or ownership in a data project."]
            return ["Project ownership evidence is limited or not clearly demonstrated."]

        if dim == "D5":
            if level >= 4:
                return ["Candidate answers were reasonably clear, specific, and structured."]
            return ["Soft-signal confidence is limited because the interview evidence is not deep enough."]

        return ["Evidence collected from interview answers."]

    def _build_strengths(self, levels: dict, dimensions: dict) -> list:
        strengths = []

        if levels.get("D1", 0) >= 4:
            strengths.append("Strong technical foundation supported by tool or SQL-related evidence.")
        if levels.get("D2", 0) >= 4:
            strengths.append("Good analytical thinking and ability to investigate metric changes.")
        if levels.get("D3", 0) >= 4:
            strengths.append("Able to connect analysis to business or stakeholder needs.")
        if levels.get("D4", 0) >= 4:
            strengths.append("Shows project ownership or hands-on project contribution.")

        if not strengths:
            strengths.append("Candidate completed the interview and provided usable responses for evaluation.")

        return strengths[:3]

    def _build_weaknesses(self, levels: dict, dimensions: dict) -> list:
        weaknesses = []

        if levels.get("D1", 3) <= 2:
            weaknesses.append("Technical answers need more specific evidence and depth.")
        if levels.get("D2", 3) <= 2:
            weaknesses.append("Analytical reasoning needs stronger structure and clearer investigation steps.")
        if levels.get("D3", 3) <= 3:
            weaknesses.append("Business impact storytelling could be improved.")
        if levels.get("D4", 3) <= 3:
            weaknesses.append("Project ownership details need more evidence.")

        return weaknesses[:3]

    def _build_risks(self, levels: dict, dimensions: dict) -> list:
        risks = []

        low_confidence_dims = [
            dim for dim, data in dimensions.items()
            if data.get("confidence") == "Low"
        ]

        if low_confidence_dims:
            risks.append(
                f"Low confidence in {', '.join(low_confidence_dims)} due to limited interview evidence."
            )

        if max(levels.values()) - min(levels.values()) >= 2:
            risks.append("Candidate profile appears uneven across evaluation dimensions.")

        if not risks:
            risks.append("No major risk flags detected in the current fallback evaluation.")

        return risks