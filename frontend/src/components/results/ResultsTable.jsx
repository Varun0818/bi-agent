import { useState } from "react";

export default function ResultsTable({ columns, rows, rowCount }) {
  const [currentPage, setCurrentPage] = useState(0);
  const rowsPerPage = 10;
  const totalPages = Math.ceil(rows.length / rowsPerPage);
  const currentRows = rows.slice(currentPage * rowsPerPage, (currentPage + 1) * rowsPerPage);
  const isNumeric = (v) => !isNaN(v) && !isNaN(parseFloat(v));

  if (rows.length === 0) {
    return (
      <div
        className="mt-3 flex items-center justify-center rounded-xl p-5 text-sm"
        style={{ background: "var(--bg-card)", border: "1px solid var(--border)", color: "var(--text-muted)" }}
      >
        No data returned.
      </div>
    );
  }

  return (
    <div
      className="mt-3 overflow-hidden rounded-xl"
      style={{ background: "var(--bg-card)", border: "1px solid var(--border)", boxShadow: "var(--shadow-card)" }}
    >
      {/* Table header bar */}
      <div
        className="flex items-center justify-between px-4 py-2.5"
        style={{ borderBottom: "1px solid var(--border)" }}
      >
        <span
          className="rounded-full px-2.5 py-0.5 text-xs font-semibold text-white"
          style={{ background: "var(--brand)" }}
        >
          {rowCount} rows
        </span>
        {totalPages > 1 && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setCurrentPage((p) => Math.max(0, p - 1))}
              disabled={currentPage === 0}
              className="rounded-lg px-2.5 py-1 text-xs font-medium disabled:opacity-40"
              style={{ background: "var(--bg-hover)", color: "var(--text-secondary)", transition: "opacity 0.15s" }}
            >
              ‹ Prev
            </button>
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>
              {currentPage + 1} / {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setCurrentPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={currentPage === totalPages - 1}
              className="rounded-lg px-2.5 py-1 text-xs font-medium disabled:opacity-40"
              style={{ background: "var(--bg-hover)", color: "var(--text-secondary)", transition: "opacity 0.15s" }}
            >
              Next ›
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)" }}>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wider"
                  style={{ color: "var(--text-muted)", background: "var(--bg-secondary)" }}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentRows.map((row, ri) => (
              <tr
                key={ri}
                style={{
                  background: ri % 2 === 0 ? "var(--bg-card)" : "var(--bg-secondary)",
                  borderBottom: "1px solid var(--border)",
                  transition: "background 0.12s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--bg-hover)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = ri % 2 === 0 ? "var(--bg-card)" : "var(--bg-secondary)")}
              >
                {columns.map((col) => (
                  <td
                    key={`${ri}-${col}`}
                    className={`whitespace-nowrap px-4 py-3 text-xs ${isNumeric(row[col]) ? "text-right font-mono" : "text-left"}`}
                    style={{ color: "var(--text-primary)" }}
                  >
                    {row[col] ?? "—"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
