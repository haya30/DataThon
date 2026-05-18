import asyncio

from app.services.agent_orchestrator import NukhbaAgent


async def test():
    agent = NukhbaAgent()

    cv_text = """
Sara is a junior data analyst with experience in SQL, Excel, and Power BI.
She built a sales dashboard, cleaned customer transaction data,
and created monthly performance reports.
"""

    questions_result = await agent.generate_interview_questions(
        cv_text=cv_text,
        language="English"
    )

    questions = questions_result["questions"]

    print("\nGenerated Questions:")
    for question in questions:
        print(question)

    session = agent.create_interview_session(questions)

    print("\nFirst Question:")
    print(session.get_current_question())

    session.submit_answer(
        "I would join the users table with the events table, group activity by month, and count distinct user IDs."
    )

    session.submit_answer(
        "I cleaned missing values, removed duplicates, standardized date formats, and validated totals against source reports."
    )

    session.submit_answer(
        "I would segment sales by region, product, and customer type, then check conversion and order value changes."
    )

    session.submit_answer(
        "I would explain the main trend first, then connect it to business impact and recommend an action."
    )

    final_result = session.submit_answer(
        "I owned a dashboard project from requirements gathering to delivery and stakeholder review."
    )

    answers = final_result["answers"]

    result = await agent.evaluate_candidate(
        candidate_name="Sara Mohammed",
        job_role="Data Analyst",
        answers=answers,
        cv_text=cv_text,
        job_description="Data Analyst role requiring SQL, dashboards, data cleaning, statistics, and insight communication."
    )

    print("\nFinal Evaluation:")
    print(result["evaluation"])

    print("\nHR Report:")
    print(result["report"])


if __name__ == "__main__":
    asyncio.run(test())