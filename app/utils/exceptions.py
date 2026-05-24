"""Custom exceptions for the application."""


class AdaptivePrepError(Exception):
    """Base exception for all application errors."""
    pass


class PDFParsingError(AdaptivePrepError):
    """Raised when PDF extraction fails."""
    pass


class SectionNotFoundError(AdaptivePrepError):
    """Raised when requested section ID doesn't exist in PDF."""
    pass


class LLMError(AdaptivePrepError):
    """Raised when LLM call fails."""
    pass


class DatabaseError(AdaptivePrepError):
    """Raised when database operation fails."""
    pass