import time

import sqlparse

from agents.state import AgentState
from utils.sql_utils import check_forbidden_keywords, extract_table_names, validate_tables_exist

KNOWN_TABLES = ["products", "customers", "orders", "order_items", "sales_targets"]


def sql_validator_node(state: AgentState) -> AgentState:
    start_time = time.time()
    sql = state["generated_sql"]
    valid = True
    error = ""

    try:
        # 1. Empty check
        if not sql.strip():
            valid = False
            error = "SQL is empty."

        # 2. Forbidden keywords
        if valid:
            has_forbidden, forbidden_msg = check_forbidden_keywords(sql)
            if has_forbidden:
                valid = False
                error = forbidden_msg

        # 3. Must start with SELECT or WITH
        if valid:
            first_word = sql.strip().upper().split()[0]
            if first_word not in ("SELECT", "WITH"):
                valid = False
                error = f"SQL must start with SELECT or WITH, got: {first_word}"

        # 4. No multiple statements
        if valid:
            statements = [s for s in sqlparse.split(sql) if s.strip()]
            if len(statements) > 1:
                valid = False
                error = "Multiple SQL statements are not allowed."

        # 5. sqlparse parse check
        if valid:
            try:
                sqlparse.parse(sql)
            except Exception as parse_exc:
                valid = False
                error = f"SQL parse error: {parse_exc}"

        # 6. Validate table names against known schema
        if valid:
            tables = extract_table_names(sql)
            is_table_valid, table_msg = validate_tables_exist(tables, KNOWN_TABLES)
            if not is_table_valid:
                valid = False
                error = table_msg

    except Exception as e:
        valid = False
        error = f"Validation error: {e}"
        print(f"[sql_validator_node] Error: {e}")

    state["sql_is_valid"] = valid
    state["sql_error"] = error if not valid else ""

    state["trace"].append({
        "node": "sql_validator",
        "input": {"generated_sql": sql[:80]},
        "output": {
            "sql_is_valid": valid,
            "sql_error": state["sql_error"],
        },
        "latency_ms": int((time.time() - start_time) * 1000),
    })

    return state
