import time

from agents.state import AgentState


def chart_generator_node(state: AgentState) -> AgentState:
    start_time = time.time()

    try:
        row_count = state["row_count"]
        result_columns = state["result_columns"]
        query_results = state["query_results"]
        user_query = state["user_query"]

        if row_count < 1 or len(result_columns) < 2:
            state["chart_config"] = {}

            state["trace"].append({
                "node": "chart_generator",
                "input": {
                    "row_count": row_count,
                    "num_columns": len(result_columns)
                },
                "output": {
                    "chart_config": "empty"
                },
                "latency_ms": int((time.time() - start_time) * 1000),
            })

            return state

        query_lower = user_query.lower()

        # -----------------------------------
        # Better time-series detection
        # -----------------------------------

        time_keywords = [
            "trend",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "over time",
            "analysis",
            "growth",
            "timeline",
            "revenue trend",
            "sales trend"
        ]

        time_aliases = [
            "date",
            "day",
            "week",
            "month",
            "year"
        ]

        is_time_series = any(
            keyword in query_lower
            for keyword in time_keywords
        )

        # -----------------------------------
        # Better X-axis selection
        # -----------------------------------

        x_key = result_columns[0]

        # Prefer time aliases first
        for col in result_columns:
            if col.lower() in time_aliases:
                x_key = col
                break

        # Fallback to first non-numeric column
        if x_key == result_columns[0]:
            for col in result_columns:
                if query_results and col in query_results[0]:
                    val = query_results[0][col]

                    if not isinstance(val, (int, float)):
                        x_key = col
                        break

        # -----------------------------------
        # Better Y-axis selection
        # -----------------------------------

        y_key = None

        priority_metrics = [
            "revenue",
            "sales",
            "profit",
            "amount",
            "total",
            "count"
        ]

        # Prefer business metric names
        for metric in priority_metrics:
            for col in result_columns:
                if metric in col.lower():
                    y_key = col
                    break

            if y_key:
                break

        # Fallback numeric detection
        if y_key is None:
            for col in result_columns:
                if query_results and col in query_results[0]:
                    val = query_results[0][col]

                    if isinstance(val, (int, float)):
                        y_key = col
                        break

        # Cannot chart
        if y_key is None:
            state["chart_config"] = {}

            state["trace"].append({
                "node": "chart_generator",
                "input": {
                    "row_count": row_count,
                    "num_columns": len(result_columns)
                },
                "output": {
                    "chart_config": "empty_no_numeric_column"
                },
                "latency_ms": int((time.time() - start_time) * 1000),
            })

            return state

        # -----------------------------------
        # Better chart type inference
        # -----------------------------------

        chart_type = "bar"

        has_date_column = any(
            col.lower() in time_aliases
            for col in result_columns
        )

        if is_time_series or has_date_column:
            chart_type = "line"

        elif row_count <= 6 and len(result_columns) == 2:
            chart_type = "pie"

        # -----------------------------------
        # Build chart config
        # -----------------------------------

        state["chart_config"] = {
            "chart_type": chart_type,
            "chart_data": query_results[:100],
            "x_key": x_key,
            "y_key": y_key,
            "title": user_query[:60]
        }

        state["trace"].append({
            "node": "chart_generator",
            "input": {
                "row_count": row_count,
                "num_columns": len(result_columns)
            },
            "output": {
                "chart_type": chart_type,
                "x_key": x_key,
                "y_key": y_key
            },
            "latency_ms": int((time.time() - start_time) * 1000),
        })

    except Exception as e:
        state["chart_config"] = {}
        state["success"] = False
        state["error_message"] = str(e)

        print(f"[chart_generator_node] Error: {e}")

    return state