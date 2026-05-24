"""Prep routes - generate questions and submit answers."""

from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import (
    GenerateRequest,
    GenerateResponse,
    QuestionSchema,
    SubmitRequest,
    SubmitResponse,
)
from app.api.dependencies import get_generate_mcqs_use_case
from app.core.generate_mcqs import GenerateMCQs
from app.utils.logger import logger
from app.utils.exceptions import SectionNotFoundError, LLMError

router = APIRouter(prefix="/prep", tags=["preparation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_questions(
    request: GenerateRequest,
    use_case: GenerateMCQs = Depends(get_generate_mcqs_use_case),
):
    """Generate MCQs for specified sections."""
    try:
        session_id = str(uuid4())
        questions_by_section = await use_case.execute(
            section_ids=request.sections,
            num_questions_per_section=request.num_questions_per_section,
        )

        all_questions = []
        for section_id, questions in questions_by_section.items():
            for q in questions:
                all_questions.append(
                    QuestionSchema(
                        id=q.id, text=q.text, choices=q.choices, section_id=q.section_id
                    )
                )

        logger.info(
            f"Generated {len(all_questions)} questions for session {session_id}"
        )

        return GenerateResponse(
            session_id=session_id, sections=request.sections, questions=all_questions
        )

    except SectionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/submit", response_model=SubmitResponse)
async def submit_answers(
    request: SubmitRequest,
):
    """Submit answers and get scoring with clarifications."""
    raise HTTPException(
        status_code=501,
        detail=(
            "The /prep/submit API is not wired for standalone scoring yet. "
            "Use the in-process SubmitAnswers use case with the generated questions."
        ),
    )
