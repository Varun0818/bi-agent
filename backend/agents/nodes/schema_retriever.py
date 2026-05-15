import time

from agents.state import AgentState
from services.schema_service import schema_service


def schema_retriever_node(state: AgentState) -> AgentState:
    start_time = time.time()
    try:
        search_query = state["user_query"] + " " + " ".join(state["entities"])
        result = schema_service.search_schema(search_query, top_k=3)
        if not result.strip():
            result = schema_service.format_full_schema()
        state["relevant_schema"] = result

        state["trace"].append({
            "node": "schema_retriever",
            "input": {"search_query": search_query[:80]},
            "output": {"relevant_schema": result[:80]},
            "latency_ms": int((time.time() - start_time) * 1000),
        })
    except Exception as e:
        state["relevant_schema"] = schema_service.format_full_schema()
        print(f"[schema_retriever_node] Error: {e}")

    return state
