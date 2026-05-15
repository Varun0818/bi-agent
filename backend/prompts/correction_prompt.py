def get_correction_prompt(
    user_query: str,
    failed_sql: str,
    error_msg: str,
    schema: str,
) -> str:
    return f"""You fix SQLite SELECT statements. Output corrected SQL ONLY — no markdown, no prose.

Schema (use only these tables/columns):
{schema}

Original user request:
{user_query}

Failed SQL:
{failed_sql}

Database error (exact):
{error_msg}

Rules:
- SQLite syntax only; SELECT only (no INSERT/UPDATE/DELETE/DROP).
- Use only schema names above; respect types and joins implied by the schema.

Return one corrected SELECT statement only.
"""
