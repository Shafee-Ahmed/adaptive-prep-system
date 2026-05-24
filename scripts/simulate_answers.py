"""Simulate user answers for testing and evaluation."""

import random
from typing import Dict, List

from app.core.entities import Question


def simulate_answers(
    questions: List[Question],
    strategy: str = "partial"
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
            # Pick a wrong answer (any letter except correct)
            wrong_letters = [l for l in ['A', 'B', 'C', 'D'] if l != q.correct_answer]
            answers[q.id] = random.choice(wrong_letters)
    
    elif strategy == "partial":
        for q in questions:
            if random.random() < 0.6:  # 60% correct
                answers[q.id] = q.correct_answer
            else:
                wrong_letters = [l for l in ['A', 'B', 'C', 'D'] if l != q.correct_answer]
                answers[q.id] = random.choice(wrong_letters)
    
    elif strategy == "weak_focused":
        # Make specific topics wrong
        weak_topics = ["inertial suspension", "mass ceiling", "tail momentum", "cooldown", "echo lock"]
        for q in questions:
            topic_lower = (q.topic or "").lower()
            is_weak = any(wt in topic_lower for wt in weak_topics)
            
            if is_weak:
                wrong_letters = [l for l in ['A', 'B', 'C', 'D'] if l != q.correct_answer]
                answers[q.id] = random.choice(wrong_letters) if wrong_letters else 'A'
            else:
                answers[q.id] = q.correct_answer
    
    return answers