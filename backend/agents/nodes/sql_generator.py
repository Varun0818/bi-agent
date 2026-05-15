import time
import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import settings
from agents.state import AgentState
from prompts.sql_prompt import get_sql_prompt
from utils.sql_utils import sanitize_sql

# Module-level singleton
llm = ChatGroq(
    model=settings.llm_model,
    api_key=settings.groq_api_key,
    temperature=0
)


def sql_generator_node(state: AgentState) -> AgentState:
    try:
        start_time = time.time()

        prompt = get_sql_prompt(
            state["user_query"],
            state["relevant_schema"],
            state["conversation_history"],
        )

        result = llm.invoke([HumanMessage(content=prompt)])
        cleaned_sql = sanitize_sql(result.content)

        state["generated_sql"] = cleaned_sql

        state["trace"].append({
            "node": "sql_generator",
            "input": {
                "query": state["user_query"][:80],
                "schema": state["relevant_schema"][:80],
            },
            "output": {"generated_sql": cleaned_sql[:80]},
            "latency_ms": int((time.time() - start_time) * 1000),
        })

    except Exception as e:
        state["generated_sql"] = ""
        state["sql_error"] = str(e)
        print(f"[sql_generator_node] Error: {e}")

    return state
