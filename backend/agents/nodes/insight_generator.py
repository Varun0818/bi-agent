import time
import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import settings
from agents.state import AgentState
from prompts.insight_prompt import get_insight_prompt

# Module-level singleton
llm = ChatGroq(
    model=settings.llm_model,
    api_key=settings.groq_api_key,
    temperature=0
)

def insight_generator_node(state: AgentState) -> AgentState:
    start_time = time.time()

    try:
        row_count = state["row_count"]
        if row_count == 0:
            state["insights"] = {
                "summary": "No data.",
                "insights": [],
                "key_metric": "0"
            }
            state["trace"].append({
                "node": "insight_generator",
                "input": {"row_count": row_count},
                "output": {"insights": state["insights"]["summary"]},
                "latency_ms": int((time.time() - start_time) * 1000),
            })
            return state

        # Format first 10 rows as readable table string
        results_preview = state["query_results"][:10]
        # This simple conversion will be fine for the prompt, not for strict JSON output
        preview_str = json.dumps(results_preview, indent=2)

        prompt = get_insight_prompt(
            state["user_query"],
            preview_str
        )

        result = llm.invoke([HumanMessage(content=prompt)])
        response_text = result.content

        # Strip markdown fences if present
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            parsed_insights = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed_insights = {
                "summary": f"Returned {row_count} rows.",
                "insights": [],
                "key_metric": str(row_count) + " rows"
            }

        state["insights"] = parsed_insights

        state["trace"].append({
            "node": "insight_generator",
            "input": {"row_count": row_count},
            "output": {"insights": state["insights"]["summary"][:80]},
            "latency_ms": int((time.time() - start_time) * 1000),
        })

    except Exception as e:
        state["success"] = False
        state["error_message"] = str(e)
        print(f"[insight_generator_node] Error: {e}")

    return state
