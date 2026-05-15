from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import crud
from dependencies import get_db

router = APIRouter(prefix="/history")


def _query_to_dict(row: Any) -> dict[str, Any]:
    return {
        "query_id": row.query_id,
        "session_id": row.session_id,
        "user_query": row.user_query,
        "generated_sql": row.generated_sql,
        "success": row.success,
        "retry_count": row.retry_count,
        "row_count": row.row_count,
        "latency_ms": row.latency_ms,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/")
def get_history(
    session_id: str, limit: int = 20, db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    rows = crud.get_query_history(db, session_id, limit)
    return [_query_to_dict(r) for r in rows]
