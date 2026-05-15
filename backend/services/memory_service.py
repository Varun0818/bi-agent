from db import crud
from db.database import SessionLocal


def get_conversation_history(session_id: str, limit: int = 10) -> list[dict]:
    db = SessionLocal()
    try:
        msgs = crud.get_messages(db, session_id, limit)
        return [{"role": m.role, "content": m.content} for m in msgs]
    finally:
        db.close()


def save_conversation_turn(session_id: str, user_msg: str, assistant_msg: str) -> None:
    db = SessionLocal()
    try:
        crud.save_message(db, session_id, "user", user_msg)
        crud.save_message(db, session_id, "assistant", assistant_msg)
        crud.update_session_activity(db, session_id)
    finally:
        db.close()
