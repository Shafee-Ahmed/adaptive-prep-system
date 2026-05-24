"""SQLite implementation of KBRepository."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List

from app.core.entities import AnswerResult, Session, WeakTopic
from app.core.interfaces import KBRepository
from app.utils.config import config
from app.utils.exceptions import DatabaseError
from app.utils.logger import logger


class SQLiteKBRepository(KBRepository):
    """SQLite database repository for knowledge base."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or config.DATABASE_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize database with schema."""
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise DatabaseError(f"Schema file not found: {schema_path}")

        try:
            with self._get_connection() as conn:
                with open(schema_path, "r", encoding="utf-8") as schema_file:
                    conn.executescript(schema_file.read())
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}")

    def save_session(self, session: Session) -> None:
        """Save a completed session and its answers."""
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO sessions (id, timestamp, sections, score) VALUES (?, ?, ?, ?)",
                    (
                        session.id,
                        session.timestamp.isoformat(),
                        json.dumps(session.sections),
                        session.score,
                    ),
                )

                for result in session.answer_results:
                    conn.execute(
                        """
                        INSERT INTO question_attempts 
                        (session_id, question_id, question_text, section_id, topic, 
                         user_answer, correct_answer, is_correct, clarification)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            session.id,
                            result.question_id,
                            result.question_text,
                            result.section_id,
                            result.topic,
                            result.user_answer,
                            result.correct_answer,
                            1 if result.is_correct else 0,
                            result.clarification,
                        ),
                    )

                    if not result.is_correct and result.topic:
                        self._update_topic_performance(
                            conn, result.section_id, result.topic
                        )

            logger.info(
                f"Session {session.id} saved with {len(session.answer_results)} answers"
            )
        except Exception as e:
            raise DatabaseError(f"Failed to save session: {e}")

    def _update_topic_performance(
        self, conn: sqlite3.Connection, section_id: int, topic: str
    ) -> None:
        """Update or insert topic performance record for wrong answer."""
        now = datetime.now().isoformat()

        conn.execute(
            """
            INSERT INTO topic_performance (section_id, topic, wrong_count, last_asked)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(section_id, topic) DO UPDATE SET
                wrong_count = wrong_count + 1,
                last_asked = ?
            """,
            (section_id, topic, now, now),
        )

    def get_weak_topics(self, section_ids: List[int]) -> List[WeakTopic]:
        """Get topics with wrong_count >= 2 for given sections."""
        if not section_ids:
            return []

        placeholders = ",".join("?" * len(section_ids))

        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT section_id, topic, wrong_count, last_asked
                    FROM topic_performance
                    WHERE section_id IN ({placeholders}) AND wrong_count >= 2
                    ORDER BY wrong_count DESC
                    """,
                    section_ids,
                ).fetchall()

            return [
                WeakTopic(
                    section_id=row["section_id"],
                    topic=row["topic"],
                    wrong_count=row["wrong_count"],
                    last_asked=datetime.fromisoformat(row["last_asked"]),
                )
                for row in rows
            ]
        except Exception as e:
            raise DatabaseError(f"Failed to get weak topics: {e}")

    def get_session_history(
        self, section_ids: List[int], limit: int = 10
    ) -> List[Session]:
        """Get recent sessions for given sections."""
        if not section_ids:
            return []

        placeholders = ",".join("?" * len(section_ids))

        try:
            with self._get_connection() as conn:
                # Get sessions that contain any of the requested sections
                rows = conn.execute(
                    f"""
                    SELECT id, timestamp, sections, score
                    FROM sessions
                    WHERE EXISTS (
                        SELECT 1 FROM json_each(sections) 
                        WHERE value IN ({placeholders})
                    )
                    ORDER BY timestamp DESC
                    LIMIT ?
                    """,
                    section_ids + [limit],
                ).fetchall()

                sessions = []
                for row in rows:
                    session = Session(
                        id=row["id"],
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        sections=json.loads(row["sections"]),
                        answer_results=[],
                    )

                    # Load answer results for this session
                    answers = conn.execute(
                        """
                        SELECT question_id, question_text, user_answer, correct_answer, 
                               is_correct, clarification, section_id, topic
                        FROM question_attempts
                        WHERE session_id = ?
                        """,
                        (session.id,),
                    ).fetchall()

                    for a in answers:
                        session.answer_results.append(
                            AnswerResult(
                                question_id=a["question_id"],
                                question_text=a["question_text"],
                                user_answer=a["user_answer"],
                                correct_answer=a["correct_answer"],
                                is_correct=bool(a["is_correct"]),
                                clarification=a["clarification"],
                                section_id=a["section_id"],
                                topic=a["topic"],
                            )
                        )

                    sessions.append(session)

                return sessions
        except Exception as e:
            raise DatabaseError(f"Failed to get session history: {e}")

    def get_mastered_topics(self, section_ids: List[int]) -> List[str]:
        """Get topics the user has consistently gotten correct (no wrong answers ever)."""
        if not section_ids:
            return []

        placeholders = ",".join("?" * len(section_ids))

        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    f"""
                    SELECT DISTINCT topic
                    FROM question_attempts
                    WHERE section_id IN ({placeholders})
                      AND topic IS NOT NULL
                      AND topic NOT IN (
                          SELECT DISTINCT topic
                          FROM question_attempts
                          WHERE section_id IN ({placeholders})
                            AND is_correct = 0
                            AND topic IS NOT NULL
                      )
                    """,
                    section_ids + section_ids,
                ).fetchall()

                return [row["topic"] for row in rows if row["topic"]]
        except Exception as e:
            raise DatabaseError(f"Failed to get mastered topics: {e}")
