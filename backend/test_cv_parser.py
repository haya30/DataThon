import asyncio

from app.services.cv_parser import CVParser


async def test():
    parser = CVParser()

    cv_text = """
Sara Mohammed
Data Analyst with 2 years of experience in SQL, Python, Excel, and Power BI.
She built dashboards, performed data cleaning, and worked on customer churn analysis.
She holds a Bachelor's degree in Information Technology.
"""

    result = await parser.parse(cv_text)

    print("\nParsed CV:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(test())