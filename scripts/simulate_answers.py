"""Simulate user answers for testing and evaluation."""

import random
from typing import Dict, List

from app.core.entities import Question

CHOICES = ["A", "B", "C", "D"]


def _wrong_choice(correct_answer: str) -> str:
    return random.choice([choice for choice in CHOICES if choice != correct_answer])


def simulate_answers(
    questions: List[Question], strategy: str = "partial"
) -> Dict[str, str]:
    """
    Simulate user answers for a list of questions.

    Strategies:
    - "all_correct": All answers correct
    - "all_wrong": All answers wrong
    - "partial": 60% correct, 40% wrong (random)
    - "weak_focused": Wrong on specific topics for adaptation testing
    """
    answers = {}

    if strategy == "all_correct":
        for q in questions:
            answers[q.id] = q.correct_answer

    elif strategy == "all_wrong":
        for q in questions:
            answers[q.id] = _wrong_choice(q.correct_answer)

    elif strategy == "partial":
        for q in questions:
            if random.random() < 0.6:
                answers[q.id] = q.correct_answer
            else:
                answers[q.id] = _wrong_choice(q.correct_answer)

    elif strategy == "weak_focused":
        weak_topics = [
            "inertial suspension",
            "mass ceiling",
            "tail momentum",
            "cooldown",
            "echo lock",
        ]
        for q in questions:
            topic_lower = (q.topic or "").lower()
            is_weak = any(wt in topic_lower for wt in weak_topics)

            if is_weak:
                answers[q.id] = _wrong_choice(q.correct_answer)
            else:
                answers[q.id] = q.correct_answer

    return answers
