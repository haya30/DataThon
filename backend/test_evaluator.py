import asyncio

from app.services.evaluator import Evaluator


async def test():
    evaluator = Evaluator()

    answers = [
        {
            "question_id": "Q1",
            "dimension": "D1 Technical Skills & Tools",
            "question": "Walk me through how you would write a SQL query to calculate monthly active users.",
            "answer": "I would join the users table with the events table, filter active events, group by month, and count distinct user IDs."
        },
        {
            "question_id": "Q2",
            "dimension": "D2 Analytical & Statistical Thinking",
            "question": "If sales dropped by 15% last month, how would you investigate the cause?",
            "answer": "I would segment sales by region, product, and customer group, then compare traffic, conversion rate, and average order value to find the root cause."
        },
        {
            "question_id": "Q3",
            "dimension": "D3 Business Acumen & Insight Communication",
            "question": "Explain a complex analysis to a non-technical stakeholder.",
            "answer": "I would explain the main trend first, then show the business impact and recommend clear actions without using technical jargon."
        }
    ]

    cv_text = "Junior Data Analyst with SQL, Excel, Power BI, and dashboarding experience."
    job_description = "Data Analyst role requiring SQL, data cleaning, dashboards, statistics, and insight communication."

    result = await evaluator.evaluate(
        answers=answers,
        cv_text=cv_text,
        job_description=job_description
    )

    print("\nEvaluation Result:\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(test())