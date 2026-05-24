"""Run Scenario B - three iterations with simulated answers and save outputs."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.generate_mcqs import GenerateMCQs
from app.core.submit_answers import SubmitAnswers
from app.infrastructure.db.sqlite_repository import SQLiteKBRepository
from app.infrastructure.pdf.pymupdf_parser import PyMuPDFParser
from app.infrastructure.llm.ollama_client import OllamaClient
from scripts.simulate_answers import simulate_answers
from app.utils.config import config


async def run_iteration(
    iteration_num: int,
    sections: list,
    kb_repo: SQLiteKBRepository,
    generate_use_case: GenerateMCQs,
    submit_use_case: SubmitAnswers,
    output_dir: Path,
) -> dict:
    """Run a single iteration and save outputs."""

    print(f"\n{'='*50}")
    print(f"Iteration {iteration_num}: Sections {sections}")
    print(f"{'='*50}")

    print(f"Generating questions...")
    questions_by_section = await generate_use_case.execute(
        section_ids=sections, num_questions_per_section=3
    )

    all_questions = []
    for q_list in questions_by_section.values():
        all_questions.extend(q_list)

    print(f"Generated {len(all_questions)} questions")

    if iteration_num == 1:
        strategy = "partial"
    elif iteration_num == 2:
        strategy = "weak_focused"
    else:
        strategy = "partial"

    user_answers = simulate_answers(all_questions, strategy=strategy)

    session = submit_use_case.execute_with_questions(
        session_id=f"iter{iteration_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        sections=sections,
        questions=all_questions,
        user_answers=user_answers,
    )

    print(f"Score: {session.score:.1f}%")

    questions_data = []
    for q in all_questions:
        user_answer = user_answers.get(q.id, "")
        is_correct = user_answer.upper() == q.correct_answer.upper()
        questions_data.append(
            {
                "id": q.id,
                "text": q.text,
                "choices": q.choices,
                "correct_answer": q.correct_answer,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "clarification": (
                    ""
                    if is_correct
                    else f"Correct: {q.correct_answer}. {q.explanation}"
                ),
                "section_id": q.section_id,
                "topic": q.topic,
            }
        )

    weak_topics = kb_repo.get_weak_topics(sections)
    sessions_history = kb_repo.get_session_history(sections, limit=20)

    kb_snapshot = {
        "iteration": iteration_num,
        "timestamp": datetime.now().isoformat(),
        "sections": sections,
        "weak_topics": [
            {
                "section_id": wt.section_id,
                "topic": wt.topic,
                "wrong_count": wt.wrong_count,
            }
            for wt in weak_topics
        ],
        "total_sessions_for_sections": len(sessions_history),
        "session_score": session.score,
    }

    iter_dir = output_dir / f"scenario_b_iter{iteration_num}"
    iter_dir.mkdir(parents=True, exist_ok=True)

    questions_file = iter_dir / f"questions_iter{iteration_num}.json"
    with open(questions_file, "w") as f:
        json.dump(questions_data, f, indent=2)

    snapshot_file = iter_dir / f"kb_snapshot_iter{iteration_num}.json"
    with open(snapshot_file, "w") as f:
        json.dump(kb_snapshot, f, indent=2)

    print(f"Saved outputs to {iter_dir}")

    return {
        "iteration": iteration_num,
        "sections": sections,
        "score": session.score,
        "weak_topics_count": len(weak_topics),
    }


async def main():
    """Run all three iterations of Scenario B."""

    print("\n" + "=" * 60)
    print("ADAPTIVE MCQ SYSTEM - SCENARIO B")
    print("=" * 60)

    config.ensure_directories()

    print(f"\nUsing LLM: Ollama with llama3.2:1b")
    print(f"Database: {config.DATABASE_PATH}")
    print(f"PDF: {config.PDF_PATH}")

    if not config.PDF_PATH.exists():
        print(f"\nERROR: PDF not found at {config.PDF_PATH}")
        print("Please copy SLATEFALL_DOSSIER.pdf to the data/ folder")
        return

    kb_repo = SQLiteKBRepository()
    pdf_parser = PyMuPDFParser()
    llm_client = OllamaClient()

    generate_use_case = GenerateMCQs(llm_client, kb_repo, pdf_parser)
    submit_use_case = SubmitAnswers(kb_repo)

    available = pdf_parser.get_available_sections()
    print(f"\nAvailable sections in PDF: {available}")

    iterations = [
        {"num": 1, "sections": [5, 8]},
        {"num": 2, "sections": [6, 8, 9]},
        {"num": 3, "sections": [8]},
    ]

    output_dir = Path("outputs")
    results = []

    for it in iterations:
        missing = [s for s in it["sections"] if s not in available]
        if missing:
            print(
                f"\nWARNING: Sections {missing} not found in PDF. Skipping iteration {it['num']}"
            )
            continue

        result = await run_iteration(
            iteration_num=it["num"],
            sections=it["sections"],
            kb_repo=kb_repo,
            generate_use_case=generate_use_case,
            submit_use_case=submit_use_case,
            output_dir=output_dir,
        )
        results.append(result)

    print("\n" + "=" * 60)
    print("SCENARIO B COMPLETE")
    print("=" * 60)
    for r in results:
        print(
            f"Iteration {r['iteration']}: Sections {r['sections']} - Score: {r['score']:.1f}% - Weak topics: {r['weak_topics_count']}"
        )

    print(f"\nOutputs saved to: {output_dir.absolute()}")
    print("\nTo view outputs:")
    print(f"  cat outputs/scenario_b_iter1/questions_iter1.json")
    print(f"  cat outputs/scenario_b_iter1/kb_snapshot_iter1.json")


if __name__ == "__main__":
    asyncio.run(main())
