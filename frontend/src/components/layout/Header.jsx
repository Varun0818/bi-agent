import { useSessionStore } from "../../store/sessionStore";

export default function Header() {
  const activeSessionId = useSessionStore((s) => s.activeSessionId);
  const sessions = useSessionStore((s) => s.sessions);

  const active = sessions.find((s) => s.session_id === activeSessionId);
  const title = active?.session_name?.trim() ? active.session_name : "New Conversation";

  return (
    <header
      className="flex h-14 shrink-0 items-center justify-between px-5"
      style={{
        background: "var(--bg-primary)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <h2
        className="truncate text-sm font-semibold tracking-wide"
        style={{ color: "var(--text-primary)" }}
      >
        {title}
      </h2>

      <div className="flex shrink-0 items-center gap-2">
        <span
          className="relative flex h-2 w-2"
          aria-hidden
        >
          <span
            className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60"
            style={{ background: "var(--brand)" }}
          />
          <span
            className="relative inline-flex h-2 w-2 rounded-full"
            style={{ background: "var(--brand)" }}
          />
        </span>
        <span className="text-xs font-medium" style={{ color: "var(--text-secondary)" }}>
          Connected
        </span>
      </div>
    </header>
  );
}
