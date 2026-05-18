from app.services.report_generator import ReportGenerator


def test():
    generator = ReportGenerator()

    evaluation = {
        "fit_score": 76,
        "knowledge_score": 82,
        "communication_score": 70,
        "recommendation": "Maybe",
        "dimensions": {
            "D1": {
                "level": 4,
                "confidence": "High",
                "evidence": ["Candidate explained SQL joins clearly."]
            },
            "D2": {
                "level": 4,
                "confidence": "Medium",
                "evidence": ["Candidate used segmentation and root cause analysis."]
            }
        },
        "strengths": [
            "Good technical foundation in SQL.",
            "Clear analytical thinking."
        ],
        "weaknesses": [
            "Business impact storytelling could be stronger."
        ],
        "risks": [
            "Some dimensions have medium confidence."
        ]
    }

    report = generator.generate_report(
        candidate_name="Sara Mohammed",
        job_role="Data Analyst",
        evaluation=evaluation
    )

    print("\nHR Report:\n")
    print(report)


if __name__ == "__main__":
    test()