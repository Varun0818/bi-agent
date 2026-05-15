import sys

sys.path.insert(0, ".")

import argparse
import json
import os
import time
from datetime import datetime

from agents.graph import run_agent
from services.schema_service import schema_service

schema_service.embed_schema()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BI agent benchmark evals.")
    parser.add_argument("--run-name", required=True, help="Label for this eval run.")
    args = parser.parse_args()

    bench_path = os.path.join(os.path.dirname(__file__), "benchmark_queries.json")
    with open(bench_path, encoding="utf-8") as f:
        benchmarks: list[dict] = json.load(f)

    n = len(benchmarks)
    results: list[dict] = []
    passed_n = 0
    latency_sum = 0
    zero_retry_n = 0

    for q in benchmarks:
        qid = q["id"]
        latency = 0
        retries = 0
        state: dict = {}
        err: str | None = None
        try:
            t = time.time()
            state = run_agent(q["user_query"], "eval_session", [])
            latency = int((time.time() - t) * 1000)
            retries = int(state.get("retry_count", 0) or 0)
        except Exception as e:
            err = str(e)
            state = {}

        sql = (state.get("generated_sql") or "").upper()
        sql_executed = bool(state.get("success") and not state.get("sql_error"))
        row_count = int(state.get("row_count", 0) or 0)
        lo, hi = q["expected_row_count_range"]
        row_ok = lo <= row_count <= hi
        gen_sql_lower = (state.get("generated_sql") or "").lower()
        tables_ok = all(t.lower() in gen_sql_lower for t in q["expected_tables"])
        keywords_ok = all(k.upper() in sql for k in q["expected_keywords"])
        passed = sql_executed and row_ok
        semantic_warn = bool(
            sql_executed and q["expected_row_count_range"][0] > 0 and row_count == 0
        )

        if passed:
            passed_n += 1
        latency_sum += latency
        if retries == 0:
            zero_retry_n += 1

        mark = "✅" if passed else "❌"
        warn_suffix = " | semantic_warn" if semantic_warn else ""
        print(f"{mark} {qid} | {latency}ms | {retries}{warn_suffix}")

        results.append(
            {
                "id": qid,
                "category": q.get("category"),
                "difficulty": q.get("difficulty"),
                "latency_ms": latency,
                "retries": retries,
                "sql_executed": sql_executed,
                "row_count": row_count,
                "row_ok": row_ok,
                "tables_ok": tables_ok,
                "keywords_ok": keywords_ok,
                "passed": passed,
                "semantic_warn": semantic_warn,
                "generated_sql": state.get("generated_sql", ""),
                "sql_error": state.get("sql_error", ""),
                "error": err,
            }
        )

    pass_pct = (100.0 * passed_n / n) if n else 0.0
    avg_latency = (latency_sum / n) if n else 0.0
    zero_retry_pct = (100.0 * zero_retry_n / n) if n else 0.0

    print(
        f"summary: pass_rate {passed_n}/{n} ({pass_pct:.1f}%), "
        f"avg_latency {avg_latency:.1f}ms, zero_retry {zero_retry_pct:.1f}%"
    )

    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = os.path.join("evals", "eval_results")
    os.makedirs(out_dir, exist_ok=True)
    out_name = f"{args.run_name}_{date_str}.json"
    out_path = os.path.join(out_dir, out_name)

    payload = {
        "run_name": args.run_name,
        "date": date_str,
        "pass_rate": f"{passed_n}/{n}",
        "pass_pct": round(pass_pct, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "zero_retry_pct": round(zero_retry_pct, 2),
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"saved: {out_path}")


if __name__ == "__main__":
    main()
