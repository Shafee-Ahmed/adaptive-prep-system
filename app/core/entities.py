"""Domain entities for the application."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4


@dataclass
class Question:
    """A multiple choice question."""

    id: str
    text: str
    choices: List[str]
    correct_answer: str
    explanation: str
    section_id: int
    topic: Optional[str] = None


@dataclass
class AnswerResult:
    """Result of a user answering a question."""

    question_id: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    clarification: str
    section_id: int
    topic: Optional[str] = None


@dataclass
class Session:
    """A preparation session."""

    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    sections: List[int] = field(default_factory=list)
    answer_results: List[AnswerResult] = field(default_factory=list)

    @property
    def score(self) -> float:
        """Calculate percentage score."""
        if not self.answer_results:
            return 0.0
        correct = sum(1 for r in self.answer_results if r.is_correct)
        return (correct / len(self.answer_results)) * 100


@dataclass
class WeakTopic:
    """Track a topic the user struggles with."""

    section_id: int
    topic: str
    wrong_count: int
    last_asked: datetime
