"""Ollama implementation of LLM client."""

import httpx
from typing import List

from app.infrastructure.llm.base import BaseLLMClient
from app.core.entities import Question
from app.utils.config import config
from app.utils.exceptions import LLMError
from app.utils.logger import logger


class OllamaClient(BaseLLMClient):
    """Ollama LLM client for local model inference."""

    def __init__(self, model: str = "llama3.2:1b"):
        self.model = model
        self.base_url = config.OLLAMA_HOST
        self.timeout = 60.0

    async def generate_mcqs(
        self,
        section_text: str,
        section_id: int,
        num_questions: int,
        weak_topics: List[str],
        mastered_topics: List[str] = None,
    ) -> List[Question]:
        """Generate MCQs using Ollama."""

        prompt = self._build_prompt(
            section_text=section_text,
            section_id=section_id,
            num_questions=num_questions,
            weak_topics=weak_topics,
            mastered_topics=mastered_topics or [],
        )

        logger.info(f"Generating {num_questions} MCQs for section {section_id}")
        logger.debug(f"Prompt length: {len(prompt)} chars")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 4000,
                        },
                    },
                )

                if response.status_code != 200:
                    raise LLMError(
                        f"Ollama returned {response.status_code}: {response.text}"
                    )

                result = response.json()
                generated_text = result.get("response", "")

                if not generated_text:
                    raise LLMError("Ollama returned empty response")

                logger.info(f"Generated response length: {len(generated_text)} chars")

                questions = self._parse_llm_response(generated_text, section_id)

                if len(questions) < num_questions:
                    logger.warning(
                        f"Only parsed {len(questions)} out of {num_questions} questions"
                    )

                return questions

        except httpx.TimeoutException:
            raise LLMError(f"Ollama request timed out after {self.timeout}s")
        except httpx.ConnectError:
            raise LLMError(
                f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?"
            )
        except Exception as e:
            raise LLMError(f"Ollama request failed: {e}")
