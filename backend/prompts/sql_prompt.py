import json


def get_sql_prompt(user_query: str, schema: str, history: list[dict]) -> str:
    last_two = history[-2:] if history else []
    history_block = json.dumps(last_two, ensure_ascii=False)

    resolved_query_instruction = ""

    if history and len(user_query.split()) <= 4:
        resolved_query_instruction = f"""
FOLLOW-UP QUERY RESOLUTION TASK:

Current user query:
"{user_query}"

Conversation history:
{history_block}

STEP 1:
Determine whether the current query is a continuation
of the MOST RECENT analytics request.

STEP 2:
If it IS a continuation,
mentally rewrite the FULL analytical request before writing SQL.

Examples:

Previous:
"Top 5 products by revenue"

Current:
"by region"

Resolved meaning:
"Show top 5 products by revenue by region"

---

Previous:
"Monthly sales"

Current:
"last 6 months"

Resolved meaning:
"Show monthly sales for the last 6 months"

---

IMPORTANT:
- Preserve metrics
- Preserve dimensions
- Preserve ranking intent
- Preserve aggregation intent
- Preserve filters
- Preserve time context

ONLY treat as standalone if clearly unrelated.
"""

    return f"""You write SQLite for analytics.

Output RAW SQL only.
No markdown.
No explanation.

{resolved_query_instruction}

TIME SERIES / TREND RULES:

Queries containing words like:
- trend
- daily
- weekly
- monthly
- yearly
- over time
- analysis
- growth

should generate grouped time-series SQL.

Use STRFTIME for SQLite date grouping.

Examples:

"daily sales analysis"
→ GROUP BY day

"monthly revenue"
→ GROUP BY month

"weekly sales trend"
→ GROUP BY week

"yearly revenue growth"
→ GROUP BY year

VERY IMPORTANT:
DO NOT add status filters unless explicitly requested.

GOOD:
SELECT STRFTIME('%Y-%m', o.order_date) AS month,
SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month

BAD:
WHERE o.status = 'completed'

Database Schema:
{schema}

Current User Request:
{user_query}

Recent Conversation History:
{history_block}

Hard rules:
- SELECT only.
- No INSERT, UPDATE, DELETE, DROP, PRAGMA, ATTACH, or DDL.
- Use only names from the schema above.
- Use proper JOINs.
- LIMIT 100 on row-level queries unless aggregation.
- For time-series queries ALWAYS return chronological order.
- Use aliases like:
  AS day
  AS week
  AS month
  AS year

Return ONE SQL query only.
"""