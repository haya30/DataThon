from app.services.interview_engine import InterviewEngine


def test():
    questions = [
        {
            "id": "Q1",
            "dimension": "D1 Technical Skills & Tools",
            "question": "Walk me through how you would write a SQL query to calculate monthly active users."
        },
        {
            "id": "Q2",
            "dimension": "D2 Analytical & Statistical Thinking",
            "question": "If sales dropped by 15% last month, how would you investigate the cause?"
        }
    ]

    engine = InterviewEngine(questions)

    print("\nCurrent Question:")
    print(engine.get_current_question())

    print("\nSubmitting short answer:")
    result = engine.submit_answer("I use SQL.")
    print(result)

    print("\nSubmitting follow-up answer:")
    result = engine.submit_answer(
        "In a real project, I joined the users table with the events table, grouped events by month, and counted distinct active users."
    )
    print(result)

    print("\nSubmitting second answer:")
    result = engine.submit_answer(
        "I would compare sales by region, product category, and customer segment, then check if the drop came from traffic, conversion, or pricing changes."
    )
    print(result)


if __name__ == "__main__":
    test()