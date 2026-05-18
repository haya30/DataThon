import json


class MockProvider:
    """
    Fallback provider used during development or when the real LLM is disabled.
    """

    async def chat(self, messages: list):
        user_content = ""

        for message in reversed(messages):
            if message.get("role") == "user":
                user_content = message.get("content", "")
                break

        lowered = user_content.lower()

        if "generate 5 interview questions" in lowered:
            return json.dumps({
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
            })

        if "evaluate this data analyst candidate" in lowered:
            return json.dumps({
                "dimensions": {
                    "D1": {
                        "level": 4,
                        "confidence": "High",
                        "evidence": ["Candidate explained SQL joins and monthly active user calculation."]
                    },
                    "D2": {
                        "level": 4,
                        "confidence": "Medium",
                        "evidence": ["Candidate mentioned segmentation and root cause analysis."]
                    },
                    "D3": {
                        "level": 3,
                        "confidence": "Medium",
                        "evidence": ["Candidate explained insights but business impact was not deeply quantified."]
                    },
                    "D4": {
                        "level": 3,
                        "confidence": "Medium",
                        "evidence": ["Candidate described project experience but ownership details are limited."]
                    },
                    "D5": {
                        "level": 4,
                        "confidence": "High",
                        "evidence": ["Answers are clear, structured, and consistent."]
                    }
                },
                "strengths": [
                    "Good technical foundation in SQL and data analysis.",
                    "Clear approach to investigating metric changes."
                ],
                "weaknesses": [
                    "Business impact storytelling could be stronger.",
                    "Project ownership details need more evidence."
                ],
                "risks": [
                    "Some dimensions have medium confidence due to limited interview depth."
                ]
            })

        return "Hello! I am NUKHBA, your AI interview assistant."