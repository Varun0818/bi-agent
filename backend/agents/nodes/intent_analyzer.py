import json
import time

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from config import settings
from agents.state import AgentState
from prompts.intent_prompt import get_intent_prompt

# Module-level singleton
llm = ChatGroq(
    model=settings.llm_model,
    api_key=settings.groq_api_key,
    temperature=0
)


def intent_analyzer_node(state: AgentState) -> AgentState:
    try:
        start_time = time.time()
        
        # Build prompt
        prompt = get_intent_prompt(
            state["user_query"],
            state["conversation_history"]
        )
        
        # LLM invocation
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
        
        # Parse JSON with fallback
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            parsed = {
                "intent": "data_query",
                "entities": [],
                "needs_clarification": False,
                "clarification_question": ""
            }
        
        # Update state
        state["intent"] = parsed.get("intent", "data_query")
        state["entities"] = parsed.get("entities", [])
        state["needs_clarification"] = parsed.get("needs_clarification", False)
        state["clarification_question"] = parsed.get("clarification_question", "")
        
        # Append trace
        state["trace"].append({
            "node": "intent_analyzer",
            "input": {"query": state["user_query"][:80]},
            "output": {
                "intent": parsed.get("intent", "data_query"),
                "entities": parsed.get("entities", [])
            },
            "latency_ms": int((time.time() - start_time) * 1000)
        })
        
    except Exception as e:
        # Fallback on any error
        state["intent"] = "data_query"
        state["entities"] = []
        state["needs_clarification"] = False
        state["clarification_question"] = ""
        print(f"[intent_analyzer_node] Error: {e}")
    
    return state
