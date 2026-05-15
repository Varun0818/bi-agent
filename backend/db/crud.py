import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from db.models import AssistantResult, ChatSession, ConversationHistory, QueryHistory, TraceLog, Feedback, EvalResult


# Sessions
def create_chat_session(db: Session, session_id: str, session_name: str) -> ChatSession:
    db_session = ChatSession(
        session_id=session_id, session_name=session_name, created_at=datetime.utcnow()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_chat_session(db: Session, session_id: str) -> Optional[ChatSession]:
    return db.query(ChatSession).filter(ChatSession.session_id == session_id).first()


def list_chat_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[ChatSession]:
    return db.query(ChatSession).offset(skip).limit(limit).all()


def update_session_activity(db: Session, session_id: str) -> Optional[ChatSession]:
    db_session = get_chat_session(db, session_id)
    if db_session:
        db_session.last_active = datetime.utcnow()
        db_session.message_count += 1
        db.commit()
        db.refresh(db_session)
    return db_session


def update_session_name(db: Session, session_id: str, name: str) -> None:
    name = name.strip()[:60]
    if not name:
        return
    db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).update({"session_name": name})
    db.commit()


# History
def save_message(
    db: Session, session_id: str, role: str, content: str
) -> ConversationHistory:
    db_message = ConversationHistory(
        session_id=session_id, role=role, content=content, created_at=datetime.utcnow()
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages(db: Session, session_id: str, limit: int = 100) -> List[ConversationHistory]:
    return (
        db.query(ConversationHistory)
        .filter(ConversationHistory.session_id == session_id)
        .order_by(ConversationHistory.created_at)
        .limit(limit)
        .all()
    )


# Queries
def save_query_history(
    db: Session,
    query_id: str,
    session_id: str,
    user_query: str,
    generated_sql: Optional[str] = None,
    success: Optional[bool] = None,
    retry_count: int = 0,
    row_count: Optional[int] = None,
    latency_ms: Optional[int] = None,
) -> QueryHistory:
    db_query = QueryHistory(
        query_id=query_id,
        session_id=session_id,
        user_query=user_query,
        generated_sql=generated_sql,
        success=success,
        retry_count=retry_count,
        row_count=row_count,
        latency_ms=latency_ms,
        created_at=datetime.utcnow()
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query


def get_query_history(db: Session, session_id: str, limit: int = 100) -> List[QueryHistory]:
    return (
        db.query(QueryHistory)
        .filter(QueryHistory.session_id == session_id)
        .order_by(QueryHistory.created_at.desc())
        .limit(limit)
        .all()
    )


# Traces
def save_trace_step(
    db: Session,
    query_id: str,
    node_name: str,
    input_data: str,
    output_data: str,
    latency_ms: int,
    step_order: int,
    token_count: Optional[int] = None,
) -> TraceLog:
    db_trace = TraceLog(
        query_id=query_id,
        node_name=node_name,
        input_data=input_data,
        output_data=output_data,
        latency_ms=latency_ms,
        token_count=token_count,
        step_order=step_order,
        created_at=datetime.utcnow()
    )
    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)
    return db_trace


def get_trace(db: Session, query_id: str) -> List[TraceLog]:
    return (
        db.query(TraceLog)
        .filter(TraceLog.query_id == query_id)
        .order_by(TraceLog.step_order)
        .all()
    )


# Feedback
def save_feedback(
    db: Session, query_id: str, rating: int, comment: Optional[str] = None
) -> Feedback:
    db_feedback = Feedback(
        query_id=query_id, rating=rating, comment=comment, created_at=datetime.utcnow()
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


# Eval
def save_eval_result(
    db: Session,
    run_name: str,
    query_ref: str,
    test_query: str,
    expected_pattern: str,
    passed: bool,
    latency_ms: int,
    retry_count: int,
    generated_sql: Optional[str] = None,
) -> EvalResult:
    db_eval = EvalResult(
        run_name=run_name,
        query_ref=query_ref,
        test_query=test_query,
        generated_sql=generated_sql,
        expected_pattern=expected_pattern,
        passed=passed,
        latency_ms=latency_ms,
        retry_count=retry_count,
        created_at=datetime.utcnow()
    )
    db.add(db_eval)
    db.commit()
    db.refresh(db_eval)
    return db_eval


def get_eval_results(db: Session, run_name: str, skip: int = 0, limit: int = 100) -> List[EvalResult]:
    return (
        db.query(EvalResult)
        .filter(EvalResult.run_name == run_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


# Assistant Results
def save_assistant_result(
    db: Session,
    session_id: str,
    query_id: str,
    result_dict: dict,
    turn_index: int = 0,
) -> None:
    obj = AssistantResult(
        session_id=session_id,
        query_id=query_id,
        result_json=json.dumps(result_dict, default=str),
        turn_index=turn_index,
        created_at=datetime.utcnow(),
    )
    db.add(obj)
    db.commit()


def get_session_results(db: Session, session_id: str) -> dict:
    """Returns {query_id: parsed_result_dict} for the session ordered by turn_index."""
    rows = (
        db.query(AssistantResult)
        .filter(AssistantResult.session_id == session_id)
        .order_by(AssistantResult.turn_index)
        .all()
    )
    return {r.query_id: json.loads(r.result_json) for r in rows}


def delete_session_cascade(db: Session, session_id: str) -> bool:
    """Deletes session + all related data. Returns True if session existed."""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()
    if not session:
        return False
    query_ids = [
        q.query_id
        for q in db.query(QueryHistory).filter(
            QueryHistory.session_id == session_id
        ).all()
    ]
    if query_ids:
        db.query(TraceLog).filter(
            TraceLog.query_id.in_(query_ids)
        ).delete(synchronize_session=False)
    db.query(AssistantResult).filter(
        AssistantResult.session_id == session_id
    ).delete(synchronize_session=False)
    db.query(QueryHistory).filter(
        QueryHistory.session_id == session_id
    ).delete(synchronize_session=False)
    db.query(ConversationHistory).filter(
        ConversationHistory.session_id == session_id
    ).delete(synchronize_session=False)
    db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).delete(synchronize_session=False)
    db.commit()
    return True


def delete_all_sessions(db: Session) -> int:
    """Deletes ALL sessions. Returns count deleted."""
    all_ids = [s.session_id for s in db.query(ChatSession).all()]
    if not all_ids:
        return 0
    db.query(TraceLog).filter(
        TraceLog.query_id.in_(
            db.query(QueryHistory.query_id).filter(
                QueryHistory.session_id.in_(all_ids)
            )
        )
    ).delete(synchronize_session=False)
    db.query(AssistantResult).delete(synchronize_session=False)
    db.query(QueryHistory).filter(
        QueryHistory.session_id.in_(all_ids)
    ).delete(synchronize_session=False)
    db.query(ConversationHistory).filter(
        ConversationHistory.session_id.in_(all_ids)
    ).delete(synchronize_session=False)
    count = db.query(ChatSession).delete(synchronize_session=False)
    db.commit()
    return count


def cleanup_garbage_sessions(db: Session) -> int:
    """Removes sessions with garbage names AND zero messages. Safe to call on startup."""
    garbage_names = {"string", "test", "new chat", ""}
    sessions = db.query(ChatSession).all()
    deleted = 0
    for s in sessions:
        name_lower = (s.session_name or "").strip().lower()
        msg_count = db.query(ConversationHistory).filter(
            ConversationHistory.session_id == s.session_id
        ).count()
        if name_lower in garbage_names and msg_count == 0:
            db.query(ChatSession).filter(
                ChatSession.session_id == s.session_id
            ).delete(synchronize_session=False)
            deleted += 1
    db.commit()
    return deleted
