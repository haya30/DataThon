from app.services.evaluator import Evaluator


def test():
    evaluator = Evaluator()

    answers = [
        {
            "dimension": "D1 Technical Skills & Tools",
            "answer": "I use SQL to join tables and calculate metrics."
        },
        {
            "dimension": "D2 Analytical & Statistical Thinking",
            "answer": "I would analyze trends, segment data, and find root causes."
        },
        {
            "dimension": "D3 Business Acumen & Insight Communication",
            "answer": "I explain insights clearly to stakeholders with examples."
        }
    ]

    result = evaluator.evaluate(answers)

    print("\nEvaluation Result:\n")
    print(result)


if __name__ == "__main__":
    test()