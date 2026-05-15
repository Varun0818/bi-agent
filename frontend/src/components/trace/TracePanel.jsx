import { useState } from "react";

function formatNodeName(node) {
  return node.split("_").map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

function LatencyBadge({ ms }) {
  const color = ms < 500
    ? { bg: "rgba(29,158,117,0.15)", text: "#1D9E75" }
    : ms < 1500
    ? { bg: "rgba(245,158,11,0.15)", text: "#F59E0B" }
    : { bg: "rgba(239,68,68,0.15)", text: "#EF4444" };

  return (
    <span
      className="rounded-full px-2 py-0.5 text-xs font-medium"
      style={{ background: color.bg, color: color.text }}
    >
      {ms} ms
    </span>
  );
}

function StepCard({ step, index }) {
  const [showInput, setShowInput] = useState(false);
  const [showOutput, setShowOutput] = useState(false);

  return (
    <div className="flex gap-3">
      {/* Timeline indicator */}
      <div className="flex flex-col items-center">
        <div
          className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
          style={{ background: "var(--brand)" }}
        >
          {index + 1}
        </div>
        <div className="mt-1 w-px flex-1" style={{ background: "var(--border)" }} />
      </div>

      {/* Step content */}
      <div className="mb-4 min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold" style={{ color: "var(--text-primary)" }}>
            {formatNodeName(step.node)}
          </span>
          <LatencyBadge ms={step.latency_ms} />
        </div>

        <div className="mt-1.5 flex gap-3 text-xs">
          <button
            type="button"
            onClick={() => setShowInput((v) => !v)}
            className="font-medium underline-offset-2 hover:underline"
            style={{ color: "var(--brand)" }}
          >
            {showInput ? "Hide input" : "Show input"}
          </button>
          <button
            type="button"
            onClick={() => setShowOutput((v) => !v)}
            className="font-medium underline-offset-2 hover:underline"
            style={{ color: "var(--brand)" }}
          >
            {showOutput ? "Hide output" : "Show output"}
          </button>
        </div>

        {showInput && (
          <pre
            className="mt-2 overflow-x-auto rounded-xl p-3 text-xs leading-relaxed"
            style={{ background: "#0D1117", color: "#9CDCFE", border: "1px solid rgba(255,255,255,0.07)" }}
          >
            {JSON.stringify(step.input, null, 2)}
          </pre>
        )}
        {showOutput && (
          <pre
            className="mt-2 overflow-x-auto rounded-xl p-3 text-xs leading-relaxed"
            style={{ background: "#0D1117", color: "#89D185", border: "1px solid rgba(255,255,255,0.07)" }}
          >
            {JSON.stringify(step.output, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}

export default function TracePanel({ trace }) {
  const [open, setOpen] = useState(false);
  if (!trace?.length) return null;

  return (
    <div
      className="mt-3 overflow-hidden rounded-xl"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border)" }}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-xs font-semibold"
        style={{
          color: "var(--text-secondary)",
          transition: "background 0.15s",
          borderBottom: open ? "1px solid var(--border)" : "none",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-hover)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "")}
      >
        <span className="flex items-center gap-2">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          View Reasoning Trace
          <span
            className="rounded-full px-2 py-0.5 text-xs"
            style={{ background: "rgba(29,158,117,0.15)", color: "var(--brand)" }}
          >
            {trace.length} steps
          </span>
        </span>
        <svg
          width="13" height="13" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5"
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s" }}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {open && (
        <div className="px-4 pt-4 pb-1">
          {trace.map((step, i) => (
            <StepCard key={i} step={step} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
