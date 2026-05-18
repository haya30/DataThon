import json


class MockProvider:
    """
    Fallback provider used during development or when the real LLM is disabled.
    It returns predictable responses so we can build and test the agent logic safely.
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

        return "Hello! I am NUKHBA, your AI interview assistant."