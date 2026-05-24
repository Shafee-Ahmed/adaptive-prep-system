"""Dependency injection for FastAPI routes."""

from app.core.generate_mcqs import GenerateMCQs
from app.core.submit_answers import SubmitAnswers
from app.infrastructure.db.sqlite_repository import SQLiteKBRepository
from app.infrastructure.pdf.pymupdf_parser import PyMuPDFParser
from app.infrastructure.llm.factory import get_llm_client
from app.utils.config import config


# Singleton instances
_kb_repository = None
_pdf_parser = None
_llm_client = None
_generate_mcqs_use_case = None
_submit_answers_use_case = None


def get_kb_repository():
    """Get or create KB repository instance."""
    global _kb_repository
    if _kb_repository is None:
        config.ensure_directories()
        _kb_repository = SQLiteKBRepository()
    return _kb_repository


def get_pdf_parser():
    """Get or create PDF parser instance."""
    global _pdf_parser
    if _pdf_parser is None:
        _pdf_parser = PyMuPDFParser()
    return _pdf_parser


def get_llm_client():
    """Get or create LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = get_llm_client()
    return _llm_client


def get_generate_mcqs_use_case():
    """Get or create GenerateMCQs use case."""
    global _generate_mcqs_use_case
    if _generate_mcqs_use_case is None:
        _generate_mcqs_use_case = GenerateMCQs(
            llm_client=get_llm_client(),
            kb_repository=get_kb_repository(),
            pdf_parser=get_pdf_parser()
        )
    return _generate_mcqs_use_case


def get_submit_answers_use_case():
    """Get or create SubmitAnswers use case."""
    global _submit_answers_use_case
    if _submit_answers_use_case is None:
        _submit_answers_use_case = SubmitAnswers(
            kb_repository=get_kb_repository()
        )
    return _submit_answers_use_case