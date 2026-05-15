import re
import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import Keyword

def sanitize_sql(sql: str) -> str:
    cleaned = sql.strip()
    if cleaned.startswith("```sql"):
        cleaned = cleaned[6:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    
    # Remove trailing semicolons and strip whitespace again
    cleaned = cleaned.strip()
    if cleaned.endswith(';'):
        cleaned = cleaned[:-1]
    return cleaned.strip()


def check_forbidden_keywords(sql: str) -> tuple[bool, str]:
    FORBIDDEN = [
        "DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER",
        "TRUNCATE", "EXEC", "PRAGMA", "ATTACH"
    ]
    sql_upper = sql.upper()
    for kw in FORBIDDEN:
        if re.search(r'\b' + re.escape(kw) + r'\b', sql_upper):
            return True, f"Forbidden keyword found: {kw}"
    return False, ""


def extract_table_names(sql: str) -> list[str]:
    tables = set()

    try:
        statements = sqlparse.parse(sql)

        for statement in statements:
            from_seen = False

            for token in statement.tokens:

                # Detect FROM / JOIN
                if token.ttype is Keyword and token.value.upper() in (
                    "FROM",
                    "JOIN",
                ):
                    from_seen = True
                    continue

                if not from_seen:
                    continue

                # Skip whitespace
                if token.is_whitespace:
                    continue

                # Multiple tables: FROM a, b
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        tables.add(identifier.get_real_name())
                    from_seen = False
                    continue

                # Single table
                if isinstance(token, Identifier):
                    name = token.get_real_name()
                    if name:
                        tables.add(name)
                    from_seen = False
                    continue

                # Subquery: FROM (SELECT ...)
                if token.is_group:
                    from_seen = False
                    continue

                # Reset if unexpected token
                from_seen = False

    except Exception:
        return []

    return sorted(t for t in tables if t)


def validate_tables_exist(sql_tables: list[str], known_tables: list[str]) -> tuple[bool, str]:
    known_tables_lower = {t.lower() for t in known_tables}
    for table in sql_tables:
        if table.lower() not in known_tables_lower:
            return False, f"Unknown table found: {table}"
    return True, ""
