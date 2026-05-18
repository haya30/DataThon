import json

from app.config import settings
from app.llm.mock_provider import MockProvider
from app.llm.openrouter_provider import OpenRouterProvider


class QuestionGenerator:
    """
    Generates Data Analyst interview questions.
    Uses LLM when enabled, otherwise uses smart rule-based fallback.
    """

    def __init__(self):
        self.llm = OpenRouterProvider() if settings.use_llm else MockProvider()

    async def generate_questions(
        self,
        cv_text: str,
        language: str = "English",
        parsed_cv: dict | None = None
    ) -> dict:

        parsed_cv = parsed_cv or {}

        if settings.use_llm:
            try:
                return await self._generate_with_llm(cv_text, language, parsed_cv)
            except Exception:
                print("⚠️ Question generation failed, using smart fallback")
                return self._fallback_questions(language, parsed_cv)

        return self._fallback_questions(language, parsed_cv)

    async def _generate_with_llm(self, cv_text: str, language: str, parsed_cv: dict) -> dict:
        prompt = f"""
You are NUKHBA, an AI HR Interview Agent.

Generate 5 practical interview questions for a Data Analyst candidate.

Use the CV and parsed CV profile to personalize the questions.

Cover:
1. Technical Skills: SQL, Excel, Power BI/Tableau
2. Data Cleaning
3. Analytical Thinking
4. Business Communication
5. Project Ownership

Return ONLY valid JSON.

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

Language: {language}

Parsed CV:
{json.dumps(parsed_cv, ensure_ascii=False)}

Raw CV:
{cv_text}
"""

        response = await self.llm.chat([
            {"role": "system", "content": "You are a structured interview question generator."},
            {"role": "user", "content": prompt}
        ])

        return json.loads(response)

    def _fallback_questions(self, language: str, parsed_cv: dict) -> dict:
        skills = [s.lower() for s in parsed_cv.get("skills", [])]
        tools = [t.lower() for t in parsed_cv.get("tools", [])]
        years = parsed_cv.get("experience_years")

        is_arabic = language.lower().startswith("arabic")

        has_sql = "sql" in skills
        has_python = "python" in skills
        has_powerbi = "power bi" in skills or "power bi" in tools
        has_excel = "excel" in skills or "excel" in tools

        if years is not None and years >= 4:
            ownership_question_en = "Describe a data project you owned end-to-end. How did you define success and measure impact?"
            ownership_question_ar = "صف مشروع بيانات امتلكته من البداية للنهاية. كيف حددت النجاح وقست الأثر؟"
        else:
            ownership_question_en = "Describe a data project you contributed to. What part did you personally handle?"
            ownership_question_ar = "صف مشروع بيانات شاركت فيه. ما الجزء الذي كنت مسؤولًا عنه شخصيًا؟"

        if has_sql:
            technical_question_en = "Walk me through how you would write a SQL query to calculate monthly active users using users and events tables."
            technical_question_ar = "اشرح كيف تكتب استعلام SQL لحساب عدد المستخدمين النشطين شهريًا باستخدام جدول المستخدمين وجدول الأحداث."
        elif has_excel:
            technical_question_en = "How would you use Excel to summarize monthly performance and identify unusual changes?"
            technical_question_ar = "كيف تستخدم Excel لتلخيص الأداء الشهري واكتشاف التغيرات غير الطبيعية؟"
        else:
            technical_question_en = "Which data analysis tools are you most comfortable with, and how have you used them in a real task?"
            technical_question_ar = "ما أدوات تحليل البيانات التي تجيد استخدامها، وكيف استخدمتها في مهمة حقيقية؟"

        if has_powerbi:
            communication_question_en = "Tell me about a Power BI dashboard you built. What decision did it help stakeholders make?"
            communication_question_ar = "تحدث عن لوحة Power BI بنيتها. ما القرار الذي ساعدت أصحاب المصلحة على اتخاذه؟"
        else:
            communication_question_en = "Explain a complex analysis you worked on to a non-technical stakeholder."
            communication_question_ar = "اشرح تحليلًا معقدًا عملت عليه لشخص غير تقني."

        if has_python:
            cleaning_question_en = "Tell me about a time you used Python or Pandas to clean a messy dataset. What steps did you take?"
            cleaning_question_ar = "تحدث عن مرة استخدمت فيها Python أو Pandas لتنظيف بيانات غير مرتبة. ما الخطوات التي اتبعتها؟"
        else:
            cleaning_question_en = "Tell me about a time you cleaned a messy dataset. How did you handle missing values, duplicates, or inconsistent formats?"
            cleaning_question_ar = "تحدث عن مرة نظفت فيها بيانات غير مرتبة. كيف تعاملت مع القيم المفقودة والتكرارات وتوحيد الصيغ؟"

        analytical_question_en = "If sales dropped by 15% last month, how would you investigate the root cause?"
        analytical_question_ar = "لو انخفضت المبيعات 15% الشهر الماضي، كيف ستبحث عن السبب الجذري؟"

        if is_arabic:
            questions = [
                {"id": "Q1", "dimension": "D1 Technical Skills & Tools", "question": technical_question_ar},
                {"id": "Q2", "dimension": "D1 Technical Skills & Tools", "question": cleaning_question_ar},
                {"id": "Q3", "dimension": "D2 Analytical & Statistical Thinking", "question": analytical_question_ar},
                {"id": "Q4", "dimension": "D3 Business Acumen & Insight Communication", "question": communication_question_ar},
                {"id": "Q5", "dimension": "D4 Experience & Project Ownership", "question": ownership_question_ar},
            ]
        else:
            questions = [
                {"id": "Q1", "dimension": "D1 Technical Skills & Tools", "question": technical_question_en},
                {"id": "Q2", "dimension": "D1 Technical Skills & Tools", "question": cleaning_question_en},
                {"id": "Q3", "dimension": "D2 Analytical & Statistical Thinking", "question": analytical_question_en},
                {"id": "Q4", "dimension": "D3 Business Acumen & Insight Communication", "question": communication_question_en},
                {"id": "Q5", "dimension": "D4 Experience & Project Ownership", "question": ownership_question_en},
            ]

        return {"questions": questions}