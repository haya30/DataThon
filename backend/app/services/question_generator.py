import json

from app.config import settings
from app.llm.mock_provider import MockProvider
from app.llm.openrouter_provider import OpenRouterProvider


class QuestionGenerator:
    """
    Generates interview questions for a Data Analyst candidate.
    Uses MockProvider during development and OpenRouter when USE_LLM=true.
    """

    def __init__(self):
        self.llm = OpenRouterProvider() if settings.use_llm else MockProvider()

    async def generate_questions(self, cv_text: str, language: str = "English") -> dict:
        prompt = f"""
You are NUKHBA, an AI HR Interview Agent.

Generate 5 interview questions for a Data Analyst candidate.

The questions must cover:
1. Technical Skills: SQL, Excel, Power BI/Tableau
2. Data Cleaning
3. Analytical Thinking
4. Business Communication
5. Project Ownership

Rules:
- Make the questions specific and practical.
- Use the candidate CV to personalize the questions.
- Return ONLY valid JSON.
- Do not add markdown.
- Do not add explanations.

Language: {language}

JSON format:
{{
  "questions": [
    {{
      "id": "Q1",
      "dimension": "D1 Technical Skills & Tools",
      "question": "..."
    }}
  ]
}}

Candidate CV:
{cv_text}
"""

        try:
            response = await self.llm.chat([
                {
                    "role": "system",
                    "content": "You are a structured interview question generator."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ])

            return json.loads(response)

        except Exception:
            return self._fallback_questions(language)

    def _fallback_questions(self, language: str) -> dict:
        if language.lower().startswith("arabic"):
            return {
                "questions": [
                    {
                        "id": "Q1",
                        "dimension": "D1 Technical Skills & Tools",
                        "question": "اشرح كيف تكتب استعلام SQL لحساب عدد المستخدمين النشطين شهريًا."
                    },
                    {
                        "id": "Q2",
                        "dimension": "D1 Technical Skills & Tools",
                        "question": "احكِ عن مرة تعاملت فيها مع بيانات غير نظيفة. كيف نظفتها؟"
                    },
                    {
                        "id": "Q3",
                        "dimension": "D2 Analytical & Statistical Thinking",
                        "question": "لو انخفضت المبيعات 15% الشهر الماضي، كيف ستبحث عن السبب؟"
                    },
                    {
                        "id": "Q4",
                        "dimension": "D3 Business Acumen & Insight Communication",
                        "question": "كيف تشرح تحليلًا معقدًا لشخص غير تقني؟"
                    },
                    {
                        "id": "Q5",
                        "dimension": "D4 Experience & Project Ownership",
                        "question": "صف مشروع بيانات عملت عليه من البداية للنهاية."
                    }
                ]
            }

        return {
            "questions": [
                {
                    "id": "Q1",
                    "dimension": "D1 Technical Skills & Tools",
                    "question": "Walk me through how you would write a SQL query to calculate monthly active users."
                },
                {
                    "id": "Q2",
                    "dimension": "D1 Technical Skills & Tools",
                    "question": "Tell me about a time you cleaned a messy dataset. What steps did you take?"
                },
                {
                    "id": "Q3",
                    "dimension": "D2 Analytical & Statistical Thinking",
                    "question": "If sales dropped by 15% last month, how would you investigate the cause?"
                },
                {
                    "id": "Q4",
                    "dimension": "D3 Business Acumen & Insight Communication",
                    "question": "Explain a complex analysis you worked on to a non-technical stakeholder."
                },
                {
                    "id": "Q5",
                    "dimension": "D4 Experience & Project Ownership",
                    "question": "Describe one data project you owned from start to finish."
                }
            ]
        }