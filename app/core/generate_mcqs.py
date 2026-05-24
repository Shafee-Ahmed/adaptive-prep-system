"""Use case: Generate MCQs for given sections."""

from typing import List, Dict
from app.core.entities import Question
from app.core.interfaces import LLMClient, KBRepository, PDFParser
from app.utils.logger import logger


class GenerateMCQs:
    """Use case for generating multiple choice questions."""

    def __init__(
        self, llm_client: LLMClient, kb_repository: KBRepository, pdf_parser: PDFParser
    ):
        self.llm_client = llm_client
        self.kb_repository = kb_repository
        self.pdf_parser = pdf_parser

    async def execute(
        self, section_ids: List[int], num_questions_per_section: int = 5
    ) -> Dict[int, List[Question]]:
        """
        Generate MCQs for requested sections.

        Returns: Dict mapping section_id -> list of questions
        """
        results = {}

        for section_id in section_ids:
            logger.info(f"Generating questions for Section {section_id}")
            section_text = self.pdf_parser.extract_section(section_id)
            weak_topics = self.kb_repository.get_weak_topics([section_id])
            weak_topic_names = [wt.topic for wt in weak_topics]
            mastered_topics = self.kb_repository.get_mastered_topics([section_id])

            logger.info(f"Section {section_id} - Weak topics: {weak_topic_names}")
            logger.info(f"Section {section_id} - Mastered topics: {mastered_topics}")

            questions = await self.llm_client.generate_mcqs(
                section_text=section_text,
                section_id=section_id,
                num_questions=num_questions_per_section,
                weak_topics=weak_topic_names,
                mastered_topics=mastered_topics,
            )

            results[section_id] = questions
            logger.info(
                f"Generated {len(questions)} questions for Section {section_id}"
            )

        return results
