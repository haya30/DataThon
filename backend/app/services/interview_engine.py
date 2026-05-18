from typing import Dict, List, Optional


class InterviewEngine:
    """
    Manages the interview flow:
    - stores questions
    - receives answers
    - adds simple follow-up questions
    - moves to the next question
    """

    def __init__(self, questions: List[Dict]):
        self.questions = questions
        self.current_index = 0
        self.answers = []
        self.follow_up_used = False

    def get_current_question(self) -> Optional[Dict]:
        if self.current_index >= len(self.questions):
            return None

        return self.questions[self.current_index]

    def submit_answer(self, answer: str) -> Dict:
        current_question = self.get_current_question()

        if current_question is None:
            return {
                "is_completed": True,
                "message": "Interview already completed.",
                "answers": self.answers
            }

        self.answers.append({
            "question_id": current_question["id"],
            "dimension": current_question["dimension"],
            "question": current_question["question"],
            "answer": answer
        })

        if self._needs_follow_up(answer) and not self.follow_up_used:
            self.follow_up_used = True

            return {
                "is_completed": False,
                "type": "follow_up",
                "question": self._generate_follow_up(current_question),
                "current_index": self.current_index,
                "answers": self.answers
            }

        self.current_index += 1
        self.follow_up_used = False

        next_question = self.get_current_question()

        if next_question is None and self.current_index >= len(self.questions):
            return {
                "is_completed": True,
                "message": "Interview completed.",
                "answers": self.answers
            }

        return {
            "is_completed": False,
            "type": "next_question",
            "question": next_question,
            "current_index": self.current_index,
            "answers": self.answers
        }

    def _needs_follow_up(self, answer: str) -> bool:
        """
        Simple rule:
        If the answer is too short, vague, or lacks examples,
        ask a follow-up question.
        """

        if not answer:
            return True

        words = answer.strip().split()

        vague_phrases = [
            "i don't know",
            "not sure",
            "maybe",
            "basic",
            "some experience"
        ]

        if len(words) < 15:
            return True

        lowered = answer.lower()

        return any(phrase in lowered for phrase in vague_phrases)

    def _generate_follow_up(self, question: Dict) -> Dict:
        """
        Generates a simple follow-up question based on the dimension.
        """

        dimension = question.get("dimension", "")

        if "D1" in dimension:
            follow_up_text = "Can you give a specific technical example from a real project?"
        elif "D2" in dimension:
            follow_up_text = "What data would you check first, and why?"
        elif "D3" in dimension:
            follow_up_text = "How would you explain the business impact of your analysis?"
        elif "D4" in dimension:
            follow_up_text = "What part of the project did you personally own?"
        else:
            follow_up_text = "Can you explain your answer with a specific example?"

        return {
            "id": f'{question["id"]}_FU',
            "dimension": question["dimension"],
            "question": follow_up_text
        }