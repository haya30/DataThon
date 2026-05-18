from collections import defaultdict

from app.services.scoring import calculate_scores, get_recommendation


class Evaluator:
    """
    Evaluates candidate answers based on simple rules (MVP version).
    Later we will enhance it with LLM.
    """

    def evaluate(self, answers: list) -> dict:

        dimension_scores = defaultdict(list)

        for item in answers:
            dimension = item["dimension"]
            answer = item["answer"]

            level = self._score_answer(answer)

            key = dimension.split()[0]  # D1, D2...
            dimension_scores[key].append(level)

        final_levels = {
            dim: round(sum(levels) / len(levels))
            for dim, levels in dimension_scores.items()
        }

        # ensure all dimensions exist
        for d in ["D1", "D2", "D3", "D4", "D5"]:
            if d not in final_levels:
                final_levels[d] = 3

        scores = calculate_scores(final_levels)

        recommendation = get_recommendation(scores["fit_score"])

        return {
            "dimensions": final_levels,
            **scores,
            "recommendation": recommendation
        }

    def _score_answer(self, answer: str) -> int:
        """
        Simple heuristic scoring
        """

        if not answer:
            return 1

        words = answer.split()

        if len(words) < 10:
            return 2
        elif len(words) < 25:
            return 3
        elif len(words) < 50:
            return 4
        else:
            return 5