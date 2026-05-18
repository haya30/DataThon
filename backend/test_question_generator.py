import asyncio

from app.services.question_generator import QuestionGenerator


async def test():
    generator = QuestionGenerator()

    cv_text = """
Sara is a junior data analyst with experience in SQL, Excel, and Power BI.
She built a sales dashboard, cleaned customer transaction data,
and created monthly performance reports.
"""

    result = await generator.generate_questions(cv_text, language="English")

    print("\nGenerated Questions:\n")
    for question in result["questions"]:
        print(f'{question["id"]} | {question["dimension"]}')
        print(question["question"])
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(test())