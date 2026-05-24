"""Knowledge base routes - get snapshots and history."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import KBSnapshotRequest, KBSnapshotResponse, WeakTopicSchema
from app.api.dependencies import get_kb_repository
from app.infrastructure.db.sqlite_repository import SQLiteKBRepository
from app.utils.logger import logger

router = APIRouter(prefix="/kb", tags=["knowledge base"])


@router.post("/snapshot", response_model=KBSnapshotResponse)
async def get_kb_snapshot(
    request: KBSnapshotRequest,
    kb_repository: SQLiteKBRepository = Depends(get_kb_repository)
):
    """Get knowledge base snapshot for specified sections."""
    try:
        # Get weak topics
        weak_topics = kb_repository.get_weak_topics(request.sections)
        
        # Get session history count
        sessions = kb_repository.get_session_history(request.sections, limit=100)
        
        weak_topic_schemas = [
            WeakTopicSchema(
                section_id=wt.section_id,
                topic=wt.topic,
                wrong_count=wt.wrong_count
            )
            for wt in weak_topics
        ]
        
        logger.info(f"KB snapshot: {len(weak_topic_schemas)} weak topics, {len(sessions)} sessions")
        
        return KBSnapshotResponse(
            sections=request.sections,
            weak_topics=weak_topic_schemas,
            total_sessions=len(sessions)
        )
        
    except Exception as e:
        logger.error(f"Error getting KB snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))