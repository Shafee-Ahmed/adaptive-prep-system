"""Use case: Submit answers, score them, and update knowledge base."""

from typing import List, Dict
from datetime import datetime

from app.core.entities import Session, AnswerResult, Question
from app.core.interfaces import KBRepository
from app.utils.logger import logger


class SubmitAnswers:
    """Use case for submitting and scoring user answers."""
    
    def __init__(self, kb_repository: KBRepository):
        self.kb_repository = kb_repository

    
    def execute_with_questions(
        self,
        session_id: str,
        sections: List[int],
        questions: List[Question],
        user_answers: Dict[str, str]  # question_id -> user_answer
    ) -> Session:
        """
        Submit answers with explicit questions list.
        
        Returns: Completed Session object.
        """
        
        answer_results = []
        correct_count = 0
        
        for question in questions:
            user_answer = user_answers.get(question.id, "")
            is_correct = (user_answer.upper() == question.correct_answer.upper())
            
            if is_correct:
                correct_count += 1
                clarification = ""
            else:
                clarification = f"Correct answer was {question.correct_answer}. {question.explanation}"
            
            answer_results.append(AnswerResult(
                question_id=question.id,
                question_text=question.text,
                user_answer=user_answer,
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                clarification=clarification,
                section_id=question.section_id,
                topic=question.topic
            ))
        
        # Create session
        session = Session(
            id=session_id,
            timestamp=datetime.now(),
            sections=sections,
            answer_results=answer_results
        )
        
        # Save to knowledge base
        self.kb_repository.save_session(session)
        
        logger.info(f"Session {session_id} completed. Score: {session.score:.1f}%")
        
        return session