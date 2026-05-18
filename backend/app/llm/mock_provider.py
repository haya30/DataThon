class MockProvider:
    """
    Fallback LLM provider used when OpenRouter is unavailable,
    rate-limited, or during local demos.
    """

    async def chat(self, messages: list):
        last_user_message = ""

        for message in reversed(messages):
            if message.get("role") == "user":
                last_user_message = message.get("content", "")
                break

        if "hello" in last_user_message.lower():
            return "Hello! I am NUKHBA, your AI interview assistant."

        return (
            "This is a mock AI response from NUKHBA. "
            "OpenRouter is currently unavailable or rate-limited, "
            "so the system is using a safe fallback response."
        )