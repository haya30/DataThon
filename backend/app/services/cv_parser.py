import json
import re

from app.config import settings
from app.llm.openrouter_provider import OpenRouterProvider


class CVParser:
    """
    Parses CV text into structured data using LLM.
    Falls back to rule-based extraction if LLM is disabled or fails.
    """

    def __init__(self):
        self.llm = OpenRouterProvider()

    async def parse(self, cv_text: str) -> dict:

        if settings.use_llm:
            try:
                return await self._parse_with_llm(cv_text)
            except Exception:
                print("⚠️ CV parsing failed, using fallback")
                return self._fallback(cv_text)

        return self._fallback(cv_text)

    async def _parse_with_llm(self, cv_text: str) -> dict:

        prompt = f"""
You are an AI CV parser.

Extract structured information from the following CV.

Return ONLY valid JSON.

JSON format:
{{
  "name": "...",
  "skills": ["...", "..."],
  "tools": ["...", "..."],
  "experience_years": number,
  "education": "...",
  "projects": ["...", "..."],
  "summary": "short summary"
}}

Rules:
- Do not guess missing fields
- Use empty lists if not found
- No explanation outside JSON

CV:
{cv_text}
"""

        response = await self.llm.chat([
            {"role": "system", "content": "You are a precise CV parser."},
            {"role": "user", "content": prompt}
        ])

        return json.loads(response)

    def _fallback(self, cv_text: str) -> dict:
        """
        Simple rule-based extraction
        """

        text = cv_text.lower()

        # -------- name --------
        name = "Unknown"
        lines = cv_text.strip().split("\n")
        if lines:
            first_line = lines[0].strip()
            if len(first_line.split()) <= 4:
                name = first_line

        # -------- skills --------
        skill_keywords = [
            "sql", "python", "excel", "power bi", "tableau",
            "statistics", "machine learning", "data analysis"
        ]

        skills = [s for s in skill_keywords if s in text]

        # -------- tools --------
        tool_keywords = ["power bi", "tableau", "excel"]
        tools = [t for t in tool_keywords if t in text]

        # -------- experience --------
        experience_years = None
        match = re.search(r"(\d+)\s+years", text)
        if match:
            experience_years = int(match.group(1))

        # -------- education --------
        education = ""
        if "bachelor" in text:
            education = "Bachelor's degree"
        elif "master" in text:
            education = "Master's degree"

        # -------- projects --------
        project_keywords = ["dashboard", "analysis", "churn", "segmentation"]
        projects = [p for p in project_keywords if p in text]

        # -------- summary --------
        summary = cv_text[:200]

        return {
            "name": name,
            "skills": skills,
            "tools": tools,
            "experience_years": experience_years,
            "education": education,
            "projects": projects,
            "summary": summary,
            "raw_text": cv_text
        }