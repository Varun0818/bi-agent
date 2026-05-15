# API Contract — POST /api/v1/chat/query

## Request
{"user_query": string, "session_id": string | null}

## Response (always HTTP 200)
{
  "query_id": string,
  "session_id": string,
  "success": boolean,
  "intent": "data_query" | "chitchat" | "clarification_needed" | "",
  "clarification_question": string,
  "generated_sql": string,
  "retry_count": number,
  "row_count": number,
  "result_columns": string[],
  "query_results": object[],
  "insights": {"summary": string, "insights": string[], "key_metric": string},
  "chart_config": {"chart_type": string, "chart_data": object[],
                   "x_key": string, "y_key": string, "title": string} | {},
  "trace": [{"node": string, "input": object, "output": object, "latency_ms": number}],
  "latency_ms": number,
  "error_message": string
}