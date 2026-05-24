"""Abstract interfaces for dependency inversion."""

from abc import ABC, abstractmethod
from typing import List
from app.core.entities import Question, AnswerResult, Session, WeakTopic


class LLMClient(ABC):
    """Interface for LLM providers (Ollama, Groq, etc.)."""
    
    @abstractmethod
    async def generate_mcqs(
        self,
        section_text: str,
        section_id: int,
        num_questions: int,
        weak_topics: List[str]
    ) -> List[Question]:
        """Generate multiple choice questions from section text."""
        pass


class KBRepository(ABC):
    """Interface for knowledge base storage."""
    
    @abstractmethod
    def save_session(self, session: Session) -> None:
        """Save a completed session."""
        pass
    
    @abstractmethod
    def get_weak_topics(self, section_ids: List[int]) -> List[WeakTopic]:
        """Get topics the user has struggled with for given sections."""
        pass
    
    @abstractmethod
    def get_session_history(self, section_ids: List[int], limit: int = 10) -> List[Session]:
        """Get recent sessions for given sections."""
        pass
    
    @abstractmethod
    def get_mastered_topics(self, section_ids: List[int]) -> List[str]:
        """Get topics the user has consistently gotten correct."""
        pass


class PDFParser(ABC):
    """Interface for PDF section extraction."""
    
    @abstractmethod
    def extract_section(self, section_id: int) -> str:
        """Extract text content for a given section number."""
        pass
    
    @abstractmethod
    def get_available_sections(self) -> List[int]:
        """Get list of available section numbers in the PDF."""
        pass
    