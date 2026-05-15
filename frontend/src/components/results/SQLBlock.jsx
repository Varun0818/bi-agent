import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

export default function SQLBlock({ sql, retryCount }) {
  const [isCollapsed, setIsCollapsed] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className="mt-3 overflow-hidden rounded-xl"
      style={{
        background: "#0D1117",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      {/* Header row */}
      <div
        className="flex cursor-pointer items-center justify-between px-4 py-2.5"
        style={{ borderBottom: isCollapsed ? "none" : "1px solid rgba(255,255,255,0.07)" }}
        onClick={() => setIsCollapsed((v) => !v)}
      >
        <div className="flex items-center gap-2">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#1D9E75" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />
          </svg>
          <span className="text-xs font-semibold" style={{ color: "#9CDCFE" }}>
            View SQL
          </span>
          {retryCount > 0 && (
            <span className="rounded-full bg-yellow-500/20 px-2 py-0.5 text-xs text-yellow-400">
              Fixed in {retryCount} attempt{retryCount > 1 ? "s" : ""}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); handleCopy(); }}
            className="rounded-lg px-2.5 py-1 text-xs font-medium"
            style={{
              background: "rgba(255,255,255,0.08)",
              color: copied ? "#1D9E75" : "#94A3B8",
              transition: "color 0.2s",
            }}
          >
            {copied ? "✓ Copied" : "Copy"}
          </button>
          <svg
            width="12" height="12" viewBox="0 0 24 24" fill="none"
            stroke="#475569" strokeWidth="2.5"
            style={{ transform: isCollapsed ? "rotate(0deg)" : "rotate(180deg)", transition: "transform 0.2s" }}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </div>

      {/* SQL code */}
      {!isCollapsed && (
        <SyntaxHighlighter
          language="sql"
          style={vscDarkPlus}
          customStyle={{
            margin: 0, padding: "14px 16px",
            background: "transparent", fontSize: "12px",
            lineHeight: "1.6",
          }}
        >
          {sql}
        </SyntaxHighlighter>
      )}
    </div>
  );
}
