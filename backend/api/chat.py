import logging
import time
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agents.graph import run_agent
from db import crud
from dependencies import get_db
from services.memory_service import get_conversation_history, save_conversation_turn
from services.trace_service import save_trace

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat")


class ChatQueryRequest(BaseModel):
    user_query: str
    session_id: Optional[str] = None


class ChatQueryResponse(BaseModel):
    query_id: str = ""
    session_id: str = ""
    success: bool = False
    intent: str = ""
    clarification_question: str = ""
    generated_sql: str = ""
    retry_count: int = 0
    row_count: int = 0
    result_columns: list[str] = Field(default_factory=list)
    query_results: list[dict[str, Any]] = Field(default_factory=list)
    insights: dict[str, Any] = Field(default_factory=dict)
    chart_config: dict[str, Any] = Field(default_factory=dict)
    trace: list[dict[str, Any]] = Field(default_factory=list)
    latency_ms: int = 0
    error_message: str = ""


@router.post("/query", response_model=ChatQueryResponse)
def query(body: ChatQueryRequest, db: Session = Depends(get_db)) -> ChatQueryResponse:
    query_id = str(uuid.uuid4())
    start = time.time()

    try:
        session_id = body.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
            crud.create_chat_session(db, session_id, "New Chat")

        history = get_conversation_history(session_id, limit=10)

        final_state = run_agent(body.user_query, session_id, history)

        latency_ms = int((time.time() - start) * 1000)

        crud.save_query_history(
            db,
            query_id,
            session_id,
            body.user_query,
            final_state.get("generated_sql", ""),
            bool(final_state.get("success")),
            final_state.get("retry_count", 0),
            final_state.get("row_count", 0),
            latency_ms,
        )

        save_trace(query_id, final_state.get("trace", []))

        if final_state.get("success"):
            save_conversation_turn(
                session_id,
                body.user_query,
                final_state.get("insights", {}).get("summary", "Done"),
            )
            try:
                turn_index = len(crud.get_messages(db, session_id, limit=100))
                result_to_store = {
                    "insights": final_state.get("insights", {}),
                    "chart_config": final_state.get("chart_config", {}),
                    "generated_sql": final_state.get("generated_sql", ""),
                    "retry_count": final_state.get("retry_count", 0),
                    "row_count": final_state.get("row_count", 0),
                    "result_columns": final_state.get("result_columns", []),
                    "query_results": final_state.get("query_results", [])[:100],
                    "trace": final_state.get("trace", []),
                    "success": bool(final_state.get("success")),
                    "error_message": final_state.get("error_message", ""),
                }
                crud.save_assistant_result(
                    db, session_id, query_id, result_to_store, turn_index
                )
            except Exception as result_err:
                logger.warning("Result persistence failed (non-critical): %s", result_err)
            try:
                msg_count = len(crud.get_messages(db, session_id, limit=3))
                if msg_count <= 2:  # First turn only (user + assistant = 2 messages)
                    auto_name = body.user_query.strip()[:50]
                    crud.update_session_name(db, session_id, auto_name)
            except Exception as name_err:
                logger.warning("Session auto-name failed: %s", name_err)

        logger.info(
            "Query|%s|%s|rows=%s|%sms",
            session_id,
            final_state.get("intent"),
            final_state.get("row_count", 0),
            latency_ms,
        )

        return ChatQueryResponse(
            query_id=query_id,
            session_id=session_id,
            success=bool(final_state.get("success")),
            intent=final_state.get("intent", ""),
            clarification_question=final_state.get("clarification_question", ""),
            generated_sql=final_state.get("generated_sql", ""),
            retry_count=final_state.get("retry_count", 0),
            row_count=final_state.get("row_count", 0),
            result_columns=final_state.get("result_columns", []),
            query_results=final_state.get("query_results", [])[:100],
            insights=final_state.get("insights", {}),
            chart_config=final_state.get("chart_config", {}),
            trace=final_state.get("trace", []),
            latency_ms=latency_ms,
            error_message=final_state.get("error_message", ""),
        )

    except Exception as e:
        logger.exception("Query failed: %s", e)
        return ChatQueryResponse(
            query_id=query_id,
            session_id=body.session_id or "",
            success=False,
            error_message=str(e),
        )
