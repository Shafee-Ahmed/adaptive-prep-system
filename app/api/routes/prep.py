"""Prep routes - generate questions and submit answers."""

from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import (
    GenerateRequest,
    GenerateResponse,
    QuestionSchema,
    SubmitRequest,
    SubmitResponse,
    AnswerResultSchema,
)
from app.api.dependencies import get_generate_mcqs_use_case, get_submit_answers_use_case
from app.core.generate_mcqs import GenerateMCQs
from app.core.submit_answers import SubmitAnswers
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

        # Generate questions
        questions_by_section = await use_case.execute(
            section_ids=request.sections,
            num_questions_per_section=request.num_questions_per_section,
        )

        # Flatten questions and attach to response
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
    use_case: SubmitAnswers = Depends(get_submit_answers_use_case),
):
    """Submit answers and get scoring with clarifications."""
    try:
        # TODO: Implement full submit logic. Currently returns empty response.
        # For now, this is a placeholder. The actual submission is handled
        # via run_scenario_b.py which uses execute_with_questions() directly.

        return SubmitResponse(session_id=request.session_id, score=0.0, results=[])

    except Exception as e:
        logger.error(f"Error submitting answers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
