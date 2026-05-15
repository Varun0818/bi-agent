import InsightCard from "./InsightCard";
import ChartPanel from "./ChartPanel";
import ResultsTable from "./ResultsTable";
import SQLBlock from "./SQLBlock";
import TracePanel from "../trace/TracePanel";

function normalize(result) {
  return {
    insights: result?.insights || { summary: "", insights: [], key_metric: "" },
    chart_config:
      result?.chart_config && Object.keys(result.chart_config || {}).length > 0
        ? result.chart_config
        : null,
    query_results: result?.query_results || [],
    result_columns: result?.result_columns || [],
    row_count: result?.row_count ?? 0,
    generated_sql: result?.generated_sql || "",
    retry_count: result?.retry_count ?? 0,
    trace: (result?.trace || []).map((t) => ({
      node: t.node || "unknown",
      input: t.input || {},
      output: t.output || {},
      latency_ms: t.latency_ms ?? 0,
    })),
    success: result?.success !== false,
    error_message: result?.error_message || "",
  };
}

export default function ResultCard({ result }) {
  const safe = normalize(result);

  if (!safe.success) {
    return (
      <div className="mt-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
        <span className="font-semibold">Error: </span>
        {safe.error_message || "An unknown error occurred."}
      </div>
    );
  }

  return (
    <div className="mt-2 space-y-3">
      {safe.insights?.summary && <InsightCard insights={safe.insights} />}
      {safe.chart_config && <ChartPanel chartConfig={safe.chart_config} />}
      {safe.query_results.length > 0 && (
        <ResultsTable
          columns={safe.result_columns}
          rows={safe.query_results}
          rowCount={safe.row_count}
        />
      )}
      {safe.generated_sql && (
        <SQLBlock sql={safe.generated_sql} retryCount={safe.retry_count} />
      )}
      {safe.trace.length > 0 && <TracePanel trace={safe.trace} />}
    </div>
  );
}
