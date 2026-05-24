"""Run Scenario A - cold-start prep over any two sections."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.generate_mcqs import GenerateMCQs
from app.core.submit_answers import SubmitAnswers
from app.infrastructure.db.sqlite_repository import SQLiteKBRepository
from app.infrastructure.pdf.pymupdf_parser import PyMuPDFParser
from app.infrastructure.llm.ollama_client import OllamaClient
from app.utils.config import config
from app.utils.logger import logger


async def main():
    print("\n" + "="*60)
    print("SCENARIO A - COLD START PREP")
    print("="*60)
    
    # Use sections 1 and 2 (or any two)
    sections = [1, 2]
    
    print(f"\nSections selected: {sections}")
    print(f"Using LLM: Ollama with llama3.2:1b")
    
    # Check PDF exists
    if not config.PDF_PATH.exists():
        print(f"\nERROR: PDF not found at {config.PDF_PATH}")
        print("Please copy SLATEFALL_DOSSIER.pdf to the data/ folder")
        return
    
    # Initialize components
    kb_repo = SQLiteKBRepository()
    pdf_parser = PyMuPDFParser()
    llm_client = OllamaClient()
    
    generate_use_case = GenerateMCQs(llm_client, kb_repo, pdf_parser)
    submit_use_case = SubmitAnswers(kb_repo)
    
    # Generate questions
    print(f"\nGenerating questions...")
    questions_by_section = await generate_use_case.execute(
        section_ids=sections,
        num_questions_per_section=3
    )
    
    # Flatten questions
    all_questions = []
    for q_list in questions_by_section.values():
        all_questions.extend(q_list)
    
    print(f"Generated {len(all_questions)} questions")
    
    if not all_questions:
        print("No questions generated. Check if LLM is running.")
        return
    
    # Simulate random answers
    user_answers = {}
    for q in all_questions:
        # Random answer between A, B, C, D
        user_answers[q.id] = random.choice(['A', 'B', 'C', 'D'])
    
    # Submit answers
    session = submit_use_case.execute_with_questions(
        session_id=f"scenario_a_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        sections=sections,
        questions=all_questions,
        user_answers=user_answers
    )
    
    print(f"\nScore: {session.score:.1f}%")
    
    # Save outputs
    output_dir = Path("outputs/scenario_a")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save questions with answers
    questions_data = []
    for q in all_questions:
        user_answer = user_answers.get(q.id, "")
        is_correct = (user_answer.upper() == q.correct_answer.upper())
        questions_data.append({
            "id": q.id,
            "text": q.text,
            "choices": q.choices,
            "correct_answer": q.correct_answer,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "clarification": "" if is_correct else f"Correct: {q.correct_answer}. {q.explanation}",
            "section_id": q.section_id,
            "topic": q.topic
        })
    
    with open(output_dir / "questions.json", "w") as f:
        json.dump(questions_data, f, indent=2)
    
    # Save KB snapshot
    weak_topics = kb_repo.get_weak_topics(sections)
    kb_snapshot = {
        "timestamp": datetime.now().isoformat(),
        "sections": sections,
        "weak_topics": [
            {"section_id": wt.section_id, "topic": wt.topic, "wrong_count": wt.wrong_count}
            for wt in weak_topics
        ],
        "session_score": session.score
    }
    
    with open(output_dir / "kb_snapshot.json", "w") as f:
        json.dump(kb_snapshot, f, indent=2)
    
    print(f"\nOutputs saved to: {output_dir.absolute()}")
    print(f"  - questions.json")
    print(f"  - kb_snapshot.json")
    print("\n" + "="*60)
    print("SCENARIO A COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())