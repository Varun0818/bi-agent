import time
import datetime
from decimal import Decimal

from sqlalchemy import create_engine, text

from agents.state import AgentState
from db.database import demo_db_path

demo_engine = create_engine(
    f"sqlite:///file:{demo_db_path}?mode=ro&uri=true",
    connect_args={"check_same_thread": False},
)


def _convert_value(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v


def sql_executor_node(state: AgentState) -> AgentState:
    start_time = time.time()

    if not state["sql_is_valid"]:
        state["trace"].append({
            "node": "sql_executor",
            "input": {"generated_sql": state["generated_sql"][:80]},
            "output": {"skipped": "skipped-invalid"},
            "latency_ms": int((time.time() - start_time) * 1000),
        })
        return state

    try:
        with demo_engine.connect() as conn:
            result = conn.execute(text(state["generated_sql"]))
            columns = list(result.keys())
            rows = result.fetchmany(500)

        rows_dicts = [
            {col: _convert_value(val) for col, val in zip(columns, row)}
            for row in rows
        ]

        state["query_results"] = rows_dicts
        state["result_columns"] = columns
        state["row_count"] = len(rows_dicts)
        state["success"] = True

    except Exception as e:
        state["success"] = False
        state["sql_error"] = str(e)
        state["sql_is_valid"] = False
        # retryable by default
        state["terminal_error"] = False
        print(f"[sql_executor_node] Error: {e}")

    state["trace"].append({
        "node": "sql_executor",
        "input": {"generated_sql": state["generated_sql"][:80]},
        "output": {
            "row_count": state.get("row_count", 0),
            "success": state.get("success", False),
        },
        "latency_ms": int((time.time() - start_time) * 1000),
    })

    return state
