from langgraph.graph import StateGraph, END

from agents.state import AgentState, get_initial_state
from agents.nodes.intent_analyzer import intent_analyzer_node
from agents.nodes.schema_retriever import schema_retriever_node
from agents.nodes.sql_generator import sql_generator_node
from agents.nodes.sql_validator import sql_validator_node
from agents.nodes.sql_executor import sql_executor_node
from agents.nodes.error_corrector import error_corrector_node
from agents.nodes.insight_generator import insight_generator_node
from agents.nodes.chart_generator import chart_generator_node
from config import settings
assert END == "__end__"

# ---------------------------------------------------------------------------
# Routing functions — pure logic, no side effects
# ---------------------------------------------------------------------------

def route_after_intent(state: AgentState) -> str:
    if state["intent"] in ["chitchat"] or state["needs_clarification"]:
        return END
    return "schema_retriever"


def route_after_validation(state: AgentState) -> str:
    return "sql_executor" if state["sql_is_valid"] else "error_corrector"


def route_after_execution(state: AgentState) -> str:
    if state.get("success") is True:
        return "insight_generator"

    if state.get("terminal_error"):
        return END

    if state.get("retry_count", 0) >= settings.max_retries:
        return END

    return "error_corrector"


def route_after_correction(state: AgentState) -> str:
    if state.get("terminal_error"):
        return END

    return "sql_validator"


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

graph = StateGraph(AgentState)

graph.add_node("intent_analyzer", intent_analyzer_node)
graph.add_node("schema_retriever", schema_retriever_node)
graph.add_node("sql_generator", sql_generator_node)
graph.add_node("sql_validator", sql_validator_node)
graph.add_node("sql_executor", sql_executor_node)
graph.add_node("error_corrector", error_corrector_node)
graph.add_node("insight_generator", insight_generator_node)
graph.add_node("chart_generator", chart_generator_node)

graph.set_entry_point("intent_analyzer")

graph.add_conditional_edges(
    "intent_analyzer",
    route_after_intent,
    {"schema_retriever": "schema_retriever", END: END},
)

graph.add_edge("schema_retriever", "sql_generator")
graph.add_edge("sql_generator", "sql_validator")

graph.add_conditional_edges(
    "sql_validator",
    route_after_validation,
    {"sql_executor": "sql_executor", "error_corrector": "error_corrector"},
)

graph.add_conditional_edges(
    "sql_executor",
    route_after_execution,
    {"insight_generator": "insight_generator", "error_corrector": "error_corrector", END: END},
)

graph.add_conditional_edges(
    "error_corrector",
    route_after_correction,
    {"sql_validator": "sql_validator", END: END},
)

graph.add_edge("insight_generator", "chart_generator")
graph.add_edge("chart_generator", END)

bi_agent_graph = graph.compile()

# ---------------------------------------------------------------------------
# Routing assertion block — runs once at import time
# ---------------------------------------------------------------------------

from agents.state import get_initial_state as _gs  # noqa: E402

_s = _gs("test", "s1", [])
_s["intent"] = "data_query"
_s["needs_clarification"] = False
assert route_after_intent(_s) == "schema_retriever", "intent route broken"

_s["sql_is_valid"] = True
assert route_after_validation(_s) == "sql_executor"

_s["sql_is_valid"] = False
assert route_after_validation(_s) == "error_corrector"

_s["success"] = True
assert route_after_execution(_s) == "insight_generator"

_s2 = _gs("t", "s1", [])
_s2["success"] = False
_s2["retry_count"] = 0
_s2["terminal_error"] = False
assert route_after_execution(_s2) == "error_corrector"

_s3 = _gs("t", "s1", [])
_s3["success"] = False
_s3["terminal_error"] = True

assert route_after_execution(_s3) == END
assert route_after_correction(_s3) == END

print("✅ All graph routing assertions passed")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_agent(
    user_query: str,
    session_id: str,
    conversation_history: list[dict],
) -> AgentState:
    state = get_initial_state(user_query, session_id, conversation_history)
    result = bi_agent_graph.invoke(state)
    return result
