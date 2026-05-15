from typing import Optional, TypedDict


class AgentState(TypedDict):
    user_query: str
    session_id: str
    conversation_history: list[dict]
    intent: str
    entities: list[str]
    needs_clarification: bool
    clarification_question: str
    relevant_schema: str
    generated_sql: str
    sql_is_valid: bool
    sql_error: str
    retry_count: int
    query_results: list[dict]
    result_columns: list[str]
    row_count: int
    insights: dict
    chart_config: dict
    trace: list[dict]
    success: Optional[bool]
    terminal_error: bool
    error_message: str


def get_initial_state(
    user_query: str,
    session_id: str,
    conversation_history: list[dict],
) -> AgentState:
    return {
        "user_query": user_query,
        "session_id": session_id,
        "conversation_history": conversation_history,
        "intent": "",
        "entities": [],
        "needs_clarification": False,
        "clarification_question": "",
        "relevant_schema": "",
        "generated_sql": "",
        "sql_is_valid": False,
        "sql_error": "",
        "retry_count": 0,
        "query_results": [],
        "result_columns": [],
        "row_count": 0,
        "insights": {},
        "chart_config": {},
        "trace": [],
        "success": None,
        "terminal_error": False,
        "error_message": "",
    }
