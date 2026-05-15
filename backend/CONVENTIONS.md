# BI Agent — Code Conventions

## Imports: always absolute from backend/ root
  CORRECT: from config import settings
  CORRECT: from agents.state import AgentState
  NEVER:   from ..state import AgentState

## LLM Pattern: all nodes use this exact pattern
  result = llm.invoke([HumanMessage(content=prompt)])
  response_text = result.content

## State Fields: defined in agents/state.py — never rename or add fields
  outside of state.py

## Trace Pattern: all nodes append this format
  state["trace"].append({
      "node": "node_name",
      "input": {"key": value},
      "output": {"key": value},
      "latency_ms": int((time.time() - start_time) * 1000)
  })

## Error Handling: all nodes wrap in try/except, never raise outward
## ChatGroq: module-level singleton, never instantiate inside functions