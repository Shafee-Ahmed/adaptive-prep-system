"""Base LLM client interface and shared utilities."""

import re
from typing import List, Optional
from uuid import uuid4

from app.core.entities import Question
from app.core.interfaces import LLMClient
from app.utils.logger import logger


class BaseLLMClient(LLMClient):
    """Base class for LLM clients with shared parsing logic."""

    def _parse_llm_response(
        self, response_text: str, section_id: int
    ) -> List[Question]:
        """Parse LLM response into Question objects."""
        questions = []

        # Split by Q1:, Q2:, etc.
        q_pattern = r"Q(\d+)[:\.]\s*(.+?)(?=Q\d+[:\.]|$)"
        matches = list(re.finditer(q_pattern, response_text, re.DOTALL))

        for match in matches:
            q_num = match.group(1)
            q_block = match.group(2)

            # Find choices - look for A), B), C), D) patterns
            choices = {}
            for letter in ["A", "B", "C", "D"]:
                choice_pattern = rf"{letter}[\)\.]\s*(.+?)(?=[A-D][\)\.]|Correct:|$)"
                choice_match = re.search(choice_pattern, q_block, re.DOTALL)
                if choice_match:
                    choices[letter] = choice_match.group(1).strip()

            if len(choices) != 4:
                logger.warning(
                    f"Question {q_num} has {len(choices)} choices, expected 4. Skipping."
                )
                continue

            # Extract correct answer
            correct_pattern = r"Correct:\s*([A-D])"
            correct_match = re.search(correct_pattern, q_block, re.IGNORECASE)
            if not correct_match:
                logger.warning(f"No correct answer found for Q{q_num}")
                continue

            correct_answer = correct_match.group(1).upper()

            # Extract explanation
            explanation_pattern = r"Explanation:\s*(.+?)(?=Q\d+[:\.]|$)"
            explanation_match = re.search(explanation_pattern, q_block, re.DOTALL)
            explanation = (
                explanation_match.group(1).strip() if explanation_match else ""
            )

            # Question text (everything before A))
            q_text = q_block.split("A)")[0].strip()

            # Create choices list in order A, B, C, D
            choices_list = [choices["A"], choices["B"], choices["C"], choices["D"]]

            # Extract topic
            topic = q_text[:50].split("?")[0][:30] if "?" in q_text else None

            questions.append(
                Question(
                    id=str(uuid4()),
                    text=q_text,
                    choices=choices_list,
                    correct_answer=correct_answer,
                    explanation=explanation,
                    section_id=section_id,
                    topic=topic,
                )
            )

        return questions

    def _build_prompt(
        self,
        section_text: str,
        section_id: int,
        num_questions: int,
        weak_topics: List[str],
        mastered_topics: List[str],
    ) -> str:
        """Build prompt for LLM to generate MCQs."""
        weak_topics_str = ", ".join(weak_topics) if weak_topics else "None"
        mastered_str = ", ".join(mastered_topics) if mastered_topics else "None"

        prompt = f"""
        You are an expert examiner testing knowledge of the SLATEFALL dossier.

        SECTION {section_id} CONTENT:
        {section_text[:3000]}

        INSTRUCTIONS:
        Generate exactly {num_questions} multiple choice questions with 4 choices each (A, B, C, D).

        CRITICAL RULES:
        - You MUST generate EXACTLY {num_questions} questions. No more, no less.
        - Each question MUST have EXACTLY 4 choices: A), B), C), D)
        - NO "E)" or "None of the above" or "All of the above"
        - Questions must be based ONLY on the section above

        ADAPTATION:
        - WEAK TOPICS (user struggles with): {weak_topics_str}
        - MASTERED TOPICS (user knows): {mastered_str}

        OUTPUT FORMAT (follow exactly, no extra text, no explanations between questions):

        Q1: [question text]
        A) [choice]
        B) [choice]
        C) [choice]
        D) [choice]
        Correct: A
        Explanation: [brief explanation]

        Q2: [question text]
        A) [choice]
        B) [choice]
        C) [choice]
        D) [choice]
        Correct: B
        Explanation: [brief explanation]

        Q3: [question text]
        A) [choice]
        B) [choice]
        C) [choice]
        D) [choice]
        Correct: C
        Explanation: [brief explanation]

        Do not add any text before Q1 or after Q3's explanation.
        Do not add choices beyond D.
        """
        return prompt

