import json


def get_intent_prompt(user_query: str, history: list[dict]) -> str:
    last_two = history[-2:] if history else []
    history_block = json.dumps(last_two, ensure_ascii=False)

    return f"""You are an intent classifier for a BI assistant.

User message:
{user_query}

Last 2 conversation turns (JSON array):
{history_block}

Classify the message and extract entities.

Rules:
- If the user asks about sales, revenue, orders, products, or customers → intent "data_query".
- If the user greets or makes small talk → intent "chitchat".
- If you cannot run a data query without missing scope (time range, metric, entity) → intent "clarification_needed", set needs_clarification true, and write clarification_question.

- Only use "clarification_needed" if the question truly cannot be answered.
- Questions about totals, counts, trends, completed orders, revenue, regions, products, or customers should default to "data_query" even if broad.

Example:
User: "How many completed orders are there?"
Output:
{{"intent":"data_query","entities":["completed orders"],"needs_clarification":false,"clarification_question":""}}

Return ONLY valid JSON with this exact shape (no markdown, no prose):
{{"intent":"","entities":[],"needs_clarification":false,"clarification_question":""}}

intent must be one of: "data_query", "clarification_needed", "chitchat".
entities: short strings (e.g. product names, date phrases) or [].
"""
