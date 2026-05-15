import time
import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import settings
from agents.state import AgentState
from prompts.correction_prompt import get_correction_prompt
from utils.sql_utils import sanitize_sql

# Module-level singleton
llm = ChatGroq(
    model=settings.llm_model,
    api_key=settings.groq_api_key,
    temperature=0
)


def error_corrector_node(state: AgentState) -> AgentState:
    state["retry_count"] += 1
    start_time = time.time()

    try:
        if state["retry_count"] >= settings.max_retries:
            state["success"] = False
            state["terminal_error"] = True
            state["error_message"] = "Could not generate valid SQL after 3 attempts. Please rephrase."
            state["trace"].append({
                "node": "error_corrector",
                "input": {"error": state["sql_error"][:80] if state["sql_error"] else ""},
                "output": {"attempt": state["retry_count"], "status": "max_retries_exceeded"},
                "latency_ms": int((time.time() - start_time) * 1000),
            })
            return state

        prompt = get_correction_prompt(
            state["user_query"],
            state["generated_sql"],
            state["sql_error"],
            state["relevant_schema"],
        )

        result = llm.invoke([HumanMessage(content=prompt)])
        corrected_sql = sanitize_sql(result.content)

        state["generated_sql"] = corrected_sql
        state["sql_is_valid"] = False  # Reset for re-validation
        state["sql_error"] = ""      # Clear error

        state["trace"].append({
            "node": "error_corrector",
            "input": {"error": state["sql_error"][:80] if state["sql_error"] else ""},
            "output": {"attempt": state["retry_count"], "generated_sql": corrected_sql[:80]},
            "latency_ms": int((time.time() - start_time) * 1000),
        })

    except Exception as e:
        state["success"] = False
        state["terminal_error"] = True
        state["error_message"] = str(e)
        print(f"[error_corrector_node] Error: {e}")

    return state
