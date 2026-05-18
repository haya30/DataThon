import httpx
from app.config import settings


class OpenRouterProvider:
    """
    Multi-model provider with fallback support.
    It tries multiple OpenRouter models and rejects broken responses.
    """

    def __init__(self):
        self.api_key = settings.openrouter_api_key

        self.models = [
            "google/gemma-4-31b-it:free",   # 🔥 الأساسي
            "qwen/qwen3-next-80b-a3b-instruct:free",
        ]

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def _is_valid_response(self, text: str) -> bool:
        """
        Reject empty or corrupted LLM responses.
        """

        if not text or len(text.strip()) < 3:
            return False

        broken_signals = [
            "====",
            "#%#%",
            "下发",
            "oak oak",
            "View as plain text"
        ]

        return not any(signal in text for signal in broken_signals)

    async def chat(self, messages: list):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "NUKHBA AI Interview Agent"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for model in self.models:
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 200
                }

                try:
                    response = await client.post(
                        self.base_url,
                        headers=headers,
                        json=payload
                    )

                    if response.status_code != 200:
                        print(f"\n⚠️ Model failed: {model} → {response.status_code}")
                        continue

                    data = response.json()
                    content = data["choices"][0]["message"]["content"]

                    if self._is_valid_response(content):
                        print(f"\n✅ Using model: {model}")
                        return content

                    print(f"\n⚠️ Model returned corrupted response: {model}")

                except Exception as error:
                    print(f"\n❌ Error with model {model}: {error}")

        raise Exception("All models failed or returned invalid responses.")