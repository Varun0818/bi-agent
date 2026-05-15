import { useState } from "react";
import { deleteSession, renameSession } from "../../api/chatApi";
import { useSessionStore } from "../../store/sessionStore";
import { useThemeStore } from "../../store/themeStore";

/* ─── Helpers ─────────────────────────────────────────────── */
function timeAgo(dateStr) {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const h = Math.floor(mins / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d === 1) return "Yesterday";
  if (d < 7) return `${d}d ago`;
  return new Date(dateStr).toLocaleDateString([], { month: "short", day: "numeric" });
}

/* ─── SVG Icon helpers ────────────────────────────────────── */
function LogoIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="28" height="28" rx="8" fill="rgba(29,158,117,0.15)" />
      <rect x="6" y="17" width="4" height="7" rx="1.5" fill="#1D9E75" />
      <rect x="12" y="12" width="4" height="12" rx="1.5" fill="#1D9E75" />
      <rect x="18" y="7" width="4" height="17" rx="1.5" fill="#1D9E75" />
    </svg>
  );
}

function SessionIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polyline points="2,12 5,8 8,10 11,5 14,7" stroke="#1D9E75" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
      <path d="M10 11v6M14 11v6" />
      <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" />
    </svg>
  );
}

function InfoIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  );
}

function ShieldIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.5 }}>
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

/* ─── Main component ──────────────────────────────────────── */
export default function Sidebar({ onSessionClick, onNewChat, onDeleteSession, onClearAll }) {
  const sessions = useSessionStore((s) => s.sessions);
  const activeSessionId = useSessionStore((s) => s.activeSessionId);
  const updateSessionName = useSessionStore((s) => s.updateSessionName);
  const setSidebarCollapsed = useSessionStore((s) => s.setSidebarCollapsed);

  const { theme, toggleTheme } = useThemeStore();

  const [collapsed, setCollapsed] = useState(false);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [renamingId, setRenamingId] = useState(null);
  const [renameValue, setRenameValue] = useState("");
  const [menuOpenId, setMenuOpenId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  function handleToggleCollapse() {
    const next = !collapsed;
    setCollapsed(next);
    setSidebarCollapsed(next);
  }

  const sortedSessions = [...sessions].sort((a, b) => {
    if (a.session_id === activeSessionId) return -1;
    if (b.session_id === activeSessionId) return 1;
    if (a.session_name === "New Chat" && b.session_name !== "New Chat") return 1;
    if (b.session_name === "New Chat" && a.session_name !== "New Chat") return -1;
    return new Date(b.last_active || 0) - new Date(a.last_active || 0);
  });

  function handleRenameSubmit(session) {
    const val = renameValue.trim();
    if (val && val !== session.session_name) {
      renameSession(session.session_id, val)
        .then(() => updateSessionName(session.session_id, val))
        .catch(console.error);
    }
    setRenamingId(null);
    setRenameValue("");
    setMenuOpenId(null);
  }

  function handleDeleteConfirm(session) {
    setDeletingId(null);
    setMenuOpenId(null);
    if (onDeleteSession) onDeleteSession(session.session_id);
  }

  async function handleClearConfirm() {
    setShowClearConfirm(false);
    if (onClearAll) await onClearAll();
  }

  /* ── Collapsed state ─────────────────────────────────────── */
  if (collapsed) {
    return (
      <aside
        className="sidebar-bg fixed left-0 top-0 flex h-screen flex-col items-center gap-3 py-4"
        style={{ width: 56, borderRight: "1px solid var(--border-sidebar)", zIndex: 40 }}
      >
        <button
          type="button"
          onClick={handleToggleCollapse}
          title="Expand"
          className="flex items-center justify-center rounded-lg p-2 hover:bg-white/10"
          style={{ color: "var(--text-muted)" }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
        <button
          type="button"
          onClick={onNewChat}
          title="New Chat"
          className="flex items-center justify-center rounded-lg hover:opacity-90"
          style={{ width: 32, height: 32, background: "var(--brand)", color: "#fff", fontSize: 18 }}
        >
          +
        </button>
        <div className="flex flex-col gap-2 overflow-y-auto pb-2">
          {sortedSessions.map((s) => {
            const active = s.session_id === activeSessionId;
            const initial = (s.session_name || "?")[0].toUpperCase();
            return (
              <button
                key={s.session_id}
                type="button"
                onClick={() => onSessionClick(s)}
                title={s.session_name || "Untitled"}
                className="flex items-center justify-center rounded-lg text-xs font-semibold hover:opacity-90"
                style={{
                  width: 32, height: 32, flexShrink: 0,
                  background: active ? "var(--brand)" : "rgba(255,255,255,0.08)",
                  color: active ? "#fff" : "var(--text-sidebar)",
                }}
              >
                {initial}
              </button>
            );
          })}
        </div>
      </aside>
    );
  }

  /* ── Expanded state ──────────────────────────────────────── */
  return (
    <aside
      className="sidebar-bg fixed left-0 top-0 flex h-screen flex-col"
      style={{ width: 256, borderRight: "1px solid var(--border-sidebar)", zIndex: 40 }}
    >
      {/* ── Header ─────────────────────────────────────────── */}
      <div
        className="flex items-center justify-between px-4 py-4"
        style={{ borderBottom: "1px solid var(--border-sidebar)" }}
      >
        <div className="flex items-center gap-3">
          <LogoIcon />
          <div>
            <p className="text-sm font-bold leading-tight" style={{ color: "var(--text-sidebar)" }}>
              BI Agent
            </p>
            <p className="text-xs leading-tight" style={{ color: "var(--text-muted)" }}>
              AI-Powered Analytics
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleToggleCollapse}
          title="Collapse"
          className="flex items-center justify-center rounded-lg p-1.5 hover:bg-white/10"
          style={{ color: "var(--text-muted)" }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
      </div>

      {/* ── New Chat ───────────────────────────────────────── */}
      <div className="px-3 pt-3 pb-2">
        <button
          type="button"
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-sm font-semibold text-white"
          style={{ background: "var(--brand)", transition: "opacity 0.15s" }}
          onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.88")}
          onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          New Chat
        </button>
      </div>

      {/* ── Sessions list ──────────────────────────────────── */}
      <nav className="flex-1 overflow-y-auto px-2 pb-2">
        <p
          className="mb-2 mt-1 px-2 text-xs font-semibold uppercase tracking-widest"
          style={{ color: "var(--text-muted)" }}
        >
          Recent Chats
        </p>

        {sortedSessions.length === 0 && (
          <p className="px-3 py-2 text-xs" style={{ color: "var(--text-muted)" }}>
            No chats yet. Start a new one!
          </p>
        )}

        <ul className="space-y-0.5">
          {sortedSessions.map((s) => {
            const active = s.session_id === activeSessionId;
            const displayName = s.session_name || "Untitled";
            const truncated = displayName.length > 20 ? `${displayName.slice(0, 20)}…` : displayName;
            const isRenaming = renamingId === s.session_id;
            const isDeleting = deletingId === s.session_id;
            const menuOpen = menuOpenId === s.session_id;

            return (
              <li key={s.session_id}>
                <div
                  className="group relative flex items-center gap-2.5 rounded-xl px-2 py-2"
                  style={{
                    background: active
                      ? "rgba(29,158,117,0.14)"
                      : "transparent",
                    borderLeft: active ? "2px solid var(--brand)" : "2px solid transparent",
                    cursor: "pointer",
                    transition: "background 0.15s",
                  }}
                  onMouseEnter={(e) => {
                    if (!active) e.currentTarget.style.background = "rgba(255,255,255,0.06)";
                  }}
                  onMouseLeave={(e) => {
                    if (!active) e.currentTarget.style.background = "transparent";
                  }}
                  onClick={() => {
                    if (!isRenaming) {
                      onSessionClick(s);
                      setMenuOpenId(null);
                    }
                  }}
                >
                  {/* Session icon */}
                  <div
                    className="flex shrink-0 items-center justify-center rounded-lg"
                    style={{ width: 30, height: 30, background: "rgba(29,158,117,0.10)" }}
                  >
                    <SessionIcon />
                  </div>

                  {/* Name / rename input */}
                  <div className="min-w-0 flex-1">
                    {isRenaming ? (
                      <input
                        autoFocus
                        value={renameValue}
                        onChange={(e) => setRenameValue(e.target.value)}
                        className="w-full rounded px-1 text-xs outline-none"
                        style={{
                          background: "rgba(255,255,255,0.12)",
                          color: "var(--text-sidebar)",
                          border: "1px solid rgba(29,158,117,0.4)",
                        }}
                        onClick={(e) => e.stopPropagation()}
                        onBlur={() => handleRenameSubmit(s)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") e.currentTarget.blur();
                          if (e.key === "Escape") { setRenamingId(null); setRenameValue(""); }
                        }}
                      />
                    ) : (
                      <>
                        <p
                          className="truncate text-xs font-medium leading-tight"
                          style={{ color: active ? "#fff" : "var(--text-sidebar)" }}
                        >
                          {truncated}
                        </p>
                        <p className="text-xs leading-tight" style={{ color: "var(--text-muted)" }}>
                          {timeAgo(s.last_active)}
                        </p>
                      </>
                    )}
                  </div>

                  {/* Three-dot menu button */}
                  {!isRenaming && (
                    <button
                      type="button"
                      title="Options"
                      onClick={(e) => {
                        e.stopPropagation();
                        setMenuOpenId(menuOpen ? null : s.session_id);
                        setDeletingId(null);
                      }}
                      className="hidden shrink-0 rounded-lg px-1.5 py-1 text-sm font-bold group-hover:flex"
                      style={{ color: "var(--text-muted)", lineHeight: 1 }}
                    >
                      ···
                    </button>
                  )}
                </div>

                {/* Inline menu */}
                {menuOpen && !isRenaming && (
                  <div
                    className="mx-2 mb-1 overflow-hidden rounded-xl"
                    style={{
                      background: "rgba(14,27,46,0.95)",
                      border: "1px solid var(--border-sidebar)",
                      boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
                    }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {!isDeleting ? (
                      <>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setRenamingId(s.session_id);
                            setRenameValue(s.session_name || "");
                            setMenuOpenId(null);
                          }}
                          className="flex w-full items-center gap-2 px-3 py-2 text-xs hover:bg-white/08"
                          style={{ color: "var(--text-sidebar)", transition: "background 0.12s" }}
                          onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.07)")}
                          onMouseLeave={(e) => (e.currentTarget.style.background = "")}
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                          </svg>
                          Rename
                        </button>
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setDeletingId(s.session_id); }}
                          className="flex w-full items-center gap-2 px-3 py-2 text-xs"
                          style={{ color: "#f87171", transition: "background 0.12s" }}
                          onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(248,113,113,0.08)")}
                          onMouseLeave={(e) => (e.currentTarget.style.background = "")}
                        >
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="3 6 5 6 21 6" /><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" /><path d="M10 11v6M14 11v6" />
                          </svg>
                          Delete
                        </button>
                      </>
                    ) : (
                      <div className="px-3 py-2">
                        <p className="mb-2 text-xs" style={{ color: "#fca5a5" }}>Delete this chat?</p>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            onClick={() => handleDeleteConfirm(s)}
                            className="flex-1 rounded-lg py-1 text-xs font-medium text-white"
                            style={{ background: "rgba(239,68,68,0.65)" }}
                          >
                            Delete
                          </button>
                          <button
                            type="button"
                            onClick={() => setDeletingId(null)}
                            className="flex-1 rounded-lg py-1 text-xs"
                            style={{ background: "rgba(255,255,255,0.1)", color: "var(--text-sidebar)" }}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      </nav>

      {/* ── Settings ───────────────────────────────────────── */}
      <div
        className="px-3 py-3"
        style={{ borderTop: "1px solid var(--border-sidebar)" }}
      >
        <p
          className="mb-2 px-1 text-xs font-semibold uppercase tracking-widest"
          style={{ color: "var(--text-muted)" }}
        >
          Settings
        </p>

        {/* Dark mode toggle */}
        <div className="flex items-center justify-between rounded-xl px-3 py-2">
          <div className="flex items-center gap-2.5" style={{ color: "var(--text-sidebar)" }}>
            <span style={{ color: "var(--text-muted)" }}>
              {theme === "dark" ? <MoonIcon /> : <SunIcon />}
            </span>
            <span className="text-xs font-medium">Dark Mode</span>
          </div>
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle dark mode"
            style={{
              position: "relative", width: 36, height: 20, borderRadius: 10, flexShrink: 0,
              background: theme === "dark" ? "var(--brand)" : "#334155",
              transition: "background 0.25s",
            }}
          >
            <span style={{
              position: "absolute", width: 14, height: 14, background: "#fff", borderRadius: "50%",
              top: 3, left: theme === "dark" ? 19 : 3, transition: "left 0.25s",
            }} />
          </button>
        </div>

        {/* Clear all */}
        {!showClearConfirm ? (
          <button
            type="button"
            onClick={() => setShowClearConfirm(true)}
            className="mt-0.5 flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium"
            style={{ color: "#f87171", transition: "background 0.12s" }}
            onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(248,113,113,0.08)")}
            onMouseLeave={(e) => (e.currentTarget.style.background = "")}
          >
            <TrashIcon />
            Clear All Chats
          </button>
        ) : (
          <div
            className="mt-1 rounded-xl px-3 py-2.5"
            style={{ background: "rgba(239,68,68,0.12)", border: "1px solid rgba(239,68,68,0.25)" }}
          >
            <p className="mb-2 text-xs leading-snug" style={{ color: "#fca5a5" }}>
              Delete all {sessions.length} chats? This cannot be undone.
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleClearConfirm}
                className="flex-1 rounded-lg py-1.5 text-xs font-semibold text-white"
                style={{ background: "rgba(239,68,68,0.65)" }}
              >
                Delete All
              </button>
              <button
                type="button"
                onClick={() => setShowClearConfirm(false)}
                className="flex-1 rounded-lg py-1.5 text-xs"
                style={{ background: "rgba(255,255,255,0.08)", color: "var(--text-sidebar)" }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* About */}
        <div
          className="mt-0.5 flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs"
          style={{ color: "var(--text-muted)", cursor: "default" }}
        >
          <InfoIcon />
          BI Agent v1.0
        </div>
      </div>

      {/* ── Footer ─────────────────────────────────────────── */}
      <div
        className="flex items-center justify-center gap-1.5 px-3 py-2.5"
        style={{ borderTop: "1px solid var(--border-sidebar)" }}
      >
        <ShieldIcon />
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
          Powered by LangGraph
        </p>
      </div>
    </aside>
  );
}
