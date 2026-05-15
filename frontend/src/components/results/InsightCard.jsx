export default function InsightCard({ insights }) {
  if (!insights?.summary) return null;

  return (
    <div
      className="mt-3 rounded-xl px-4 py-3"
      style={{
        background: "rgba(29,158,117,0.07)",
        borderLeft: "3px solid var(--brand)",
        border: "1px solid rgba(29,158,117,0.2)",
        borderLeftWidth: 3,
      }}
    >
      <p className="text-sm font-semibold leading-snug" style={{ color: "var(--text-primary)" }}>
        {insights.summary}
      </p>

      {insights.key_metric && (
        <p className="mt-1.5 text-xs" style={{ color: "var(--text-secondary)" }}>
          Key metric:{" "}
          <span className="font-bold" style={{ color: "var(--brand)" }}>
            {insights.key_metric}
          </span>
        </p>
      )}

      {insights.insights?.length > 0 && (
        <ul className="mt-2 space-y-1 pl-4 text-xs" style={{ color: "var(--text-secondary)" }}>
          {insights.insights.map((item, i) => (
            <li key={i} className="list-disc leading-snug">
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
