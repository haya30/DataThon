import asyncio
from app.llm.openrouter_provider import OpenRouterProvider
from app.llm.mock_provider import MockProvider


async def test():
    provider = OpenRouterProvider()

    try:
        response = await provider.chat([
            {"role": "system", "content": "You are NUKHBA, a helpful AI interview assistant."},
            {"role": "user", "content": "Say hello in one short sentence."}
        ])
    except Exception as error:
        print("\nOpenRouter failed. Using MockProvider instead.")
        print("Error:", error)

        mock_provider = MockProvider()
        response = await mock_provider.chat([
            {"role": "user", "content": "Say hello in one short sentence."}
        ])

    print("\nLLM Response:\n")
    print(response)


if __name__ == "__main__":
    asyncio.run(test())