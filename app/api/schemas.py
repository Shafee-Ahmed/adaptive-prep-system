"""Pydantic schemas for request/response validation."""

from typing import List, Dict, Optional
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    """Request body for /prep/generate."""

    sections: List[int]
    num_questions_per_section: int = 5


class QuestionSchema(BaseModel):
    """Question response schema."""

    id: str
    text: str
    choices: List[str]
    section_id: int


class GenerateResponse(BaseModel):
    """Response body for /prep/generate."""

    session_id: str
    sections: List[int]
    questions: List[QuestionSchema]


class SubmitRequest(BaseModel):
    """Request body for /prep/submit."""

    session_id: str
    sections: List[int]
    answers: Dict[str, str]


class AnswerResultSchema(BaseModel):
    """Single answer result."""

    question_id: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    clarification: str


class SubmitResponse(BaseModel):
    """Response body for /prep/submit."""

    session_id: str
    score: float
    results: List[AnswerResultSchema]


class KBSnapshotRequest(BaseModel):
    """Request body for /kb/snapshot."""

    sections: List[int]


class WeakTopicSchema(BaseModel):
    """Weak topic response."""

    section_id: int
    topic: str
    wrong_count: int


class KBSnapshotResponse(BaseModel):
    """Response body for /kb/snapshot."""

    sections: List[int]
    weak_topics: List[WeakTopicSchema]
    total_sessions: int
