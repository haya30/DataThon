import json
from collections import defaultdict

from app.config import settings
from app.llm.openrouter_provider import OpenRouterProvider
from app.services.scoring import calculate_scores, get_recommendation


class Evaluator:
    """
    Evaluates candidate answers using:
    - LLM if USE_LLM=true
    - Rule-based fallback if USE_LLM=false or LLM fails
    """

    def __init__(self):
        self.llm = OpenRouterProvider()

    async def evaluate(self, answers: list, cv_text: str = "", job_description: str = "") -> dict:
        """
        Main entry point for evaluation.
        """

        # ✅ إذا LLM مفعّل
        if settings.use_llm:
            try:
                return await self._evaluate_with_llm(answers, cv_text, job_description)
            except Exception:
                print("⚠️ LLM failed, using rule-based fallback")
                return self._evaluate_rule_based(answers)

        # ✅ إذا LLM غير مفعّل
        return self._evaluate_rule_based(answers)

    async def _evaluate_with_llm(self, answers: list, cv_text: str, job_description: str) -> dict:
        """
        Uses LLM to evaluate answers based on rubric.
        """

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
    "D1": {{
      "level": 4,
      "confidence": "High",
      "evidence": ["..."]
    }},
    "D2": {{
      "level": 3,
      "confidence": "Medium",
      "evidence": ["..."]
    }},
    "D3": {{
      "level": 3,
      "confidence": "Medium",
      "evidence": ["..."]
    }},
    "D4": {{
      "level": 3,
      "confidence": "Medium",
      "evidence": ["..."]
    }},
    "D5": {{
      "level": 3,
      "confidence": "Medium",
      "evidence": ["..."]
    }}
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

        # استخراج levels
        levels = {
            dim: data["level"]
            for dim, data in llm_result["dimensions"].items()
        }

        # تأكد كل الأبعاد موجودة
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
        """
        Simple fallback evaluation using heuristics.
        """

        dimension_scores = defaultdict(list)

        for item in answers:
            dimension = item["dimension"]
            answer = item["answer"]

            level = self._score_answer(answer)

            key = dimension.split()[0]  # D1, D2...
            dimension_scores[key].append(level)

        final_levels = {
            dim: round(sum(levels) / len(levels))
            for dim, levels in dimension_scores.items()
        }

        # تأكد كل الأبعاد موجودة
        for d in ["D1", "D2", "D3", "D4", "D5"]:
            final_levels.setdefault(d, 3)

        scores = calculate_scores(final_levels)
        recommendation = get_recommendation(scores["fit_score"])

        return {
            "dimensions": {
                dim: {
                    "level": level,
                    "confidence": "Low",
                    "evidence": [
                        "Rule-based fallback evaluation based on answer length and completeness."
                    ]
                }
                for dim, level in final_levels.items()
            },
            "dimension_levels": final_levels,
            "strengths": [
                "Candidate completed the interview questions."
            ],
            "weaknesses": [
                "Evaluation confidence is limited because LLM evaluation is disabled or unavailable."
            ],
            "risks": [
                "Rule-based evaluation is less accurate than rubric-based LLM evaluation."
            ],
            **scores,
            "recommendation": recommendation
        }

    def _score_answer(self, answer: str) -> int:
        """
        Basic scoring based on answer length.
        """

        if not answer:
            return 1

        words = answer.split()

        if len(words) < 10:
            return 2
        elif len(words) < 25:
            return 3
        elif len(words) < 50:
            return 4
        else:
            return 5