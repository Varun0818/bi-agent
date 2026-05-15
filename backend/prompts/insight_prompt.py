import json


def get_insight_prompt(user_query: str, results_preview: list[dict]) -> str:
    preview = json.dumps(results_preview, ensure_ascii=False)

    return f"""You summarize query results for a business user.

User question:
{user_query}

Results preview (JSON rows, may be truncated):
{preview}

Return ONLY valid JSON (no markdown, no prose) with this exact shape:
{{"summary":"","insights":[],"key_metric":""}}

- summary: one short paragraph.
- insights: 3–5 strings; each must cite specific numbers from the preview when possible.
- key_metric: one concise headline number or label (string).

"""
