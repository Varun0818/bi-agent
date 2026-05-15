import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import crud
from dependencies import get_db

router = APIRouter(prefix="/sessions")


def _session_to_dict(row: Any) -> dict[str, Any]:
    return {
        "session_id": row.session_id,
        "session_name": row.session_name,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "last_active": row.last_active.isoformat() if row.last_active else None,
        "message_count": row.message_count,
    }


class CreateSessionBody(BaseModel):
    session_name: str


class RenameRequest(BaseModel):
    session_name: str


@router.get("/")
def list_chat_sessions(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = crud.list_chat_sessions(db)
    return [_session_to_dict(r) for r in rows]


@router.post("/")
def create_session(
    body: CreateSessionBody, db: Session = Depends(get_db)
) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    row = crud.create_chat_session(db, session_id, body.session_name)
    return _session_to_dict(row)


@router.get("/{session_id}/messages")
def get_session_messages(
    session_id: str, db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    msgs = crud.get_messages(db, session_id, limit=50)
    results_map = crud.get_session_results(db, session_id)
    result_list = list(results_map.values())
    enriched: list[dict[str, Any]] = []
    assistant_idx = 0
    for m in msgs:
        entry: dict[str, Any] = {
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else "",
            "result": None,
        }
        if m.role == "assistant" and assistant_idx < len(result_list):
            entry["result"] = result_list[assistant_idx]
            assistant_idx += 1
        enriched.append(entry)
    return enriched


@router.patch("/{session_id}")
def rename_session(
    session_id: str, body: RenameRequest, db: Session = Depends(get_db)
) -> dict[str, Any]:
    if len(body.session_name.strip()) < 1:
        raise HTTPException(status_code=422, detail="session_name must not be blank")
    crud.update_session_name(db, session_id, body.session_name)
    s = crud.get_chat_session(db, session_id)
    return {
        "session_id": session_id,
        "session_name": s.session_name if s else body.session_name,
    }


@router.delete("/clear-all")
def clear_all_sessions(db: Session = Depends(get_db)) -> dict[str, Any]:
    count = crud.delete_all_sessions(db)
    return {"deleted_count": count, "message": f"Cleared {count} sessions"}


@router.post("/cleanup-garbage")
def cleanup_garbage(db: Session = Depends(get_db)) -> dict[str, Any]:
    count = crud.cleanup_garbage_sessions(db)
    return {"cleaned": count, "message": f"Removed {count} empty garbage sessions"}


@router.delete("/{session_id}")
def delete_session(
    session_id: str, db: Session = Depends(get_db)
) -> dict[str, Any]:
    deleted = crud.delete_session_cascade(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True, "session_id": session_id}
