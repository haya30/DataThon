def level_to_score(level: int) -> int:
    mapping = {
        5: 95,
        4: 82,
        3: 65,
        2: 42,
        1: 20
    }
    return mapping.get(level, 65)


def calculate_scores(dimensions: dict) -> dict:
    """
    dimensions = {
        "D1": level,
        "D2": level,
        ...
    }
    """

    scores = {k: level_to_score(v) for k, v in dimensions.items()}

    fit_score = (
        scores["D1"] * 0.30 +
        scores["D2"] * 0.25 +
        scores["D3"] * 0.20 +
        scores["D4"] * 0.15 +
        scores["D5"] * 0.10
    )

    knowledge_score = (
        scores["D1"] * 0.60 +
        scores["D2"] * 0.40
    )

    communication_score = (
        scores["D3"] * 0.70 +
        scores["D5"] * 0.30
    )

    return {
        "fit_score": round(fit_score),
        "knowledge_score": round(knowledge_score),
        "communication_score": round(communication_score)
    }


def get_recommendation(fit_score: int) -> str:
    if fit_score >= 80:
        return "Recommend"
    elif fit_score >= 65:
        return "Maybe"
    elif fit_score >= 50:
        return "Conditional"
    else:
        return "Do not recommend"