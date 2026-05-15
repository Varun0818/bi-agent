import { useEffect, useRef } from "react";
import ChatBubble from "./ChatBubble";

const SUGGESTIONS = [
  {
    label: "Show monthly revenue ",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"> 
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
        <polyline points="17 6 23 6 23 12" />
      </svg>
    ),
  },
  {
    label: "Sales by region",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
        <path d="M22 12A10 10 0 0 0 12 2v10z" />
      </svg>
    ),
  },
  {
    label: "Top 5 products by revenue",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="12" width="4" height="9" rx="1" />
        <rect x="10" y="7" width="4" height="14" rx="1" />
        <rect x="17" y="3" width="4" height="18" rx="1" />
      </svg>
    ),
  },
  {
    label: "Completed vs cancelled",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="8" cy="12" r="5" />
        <polyline points="6 12 7.5 13.5 10 10.5" />
        <circle cx="16" cy="12" r="5" />
        <line x1="14" y1="10" x2="18" y2="14" />
        <line x1="18" y1="10" x2="14" y2="14" />
      </svg>
    ),
  },
];

function HeroIcon() {
  return (
    <svg width="52" height="52" viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="8" y="30" width="8" height="16" rx="2" fill="#1D9E75" />
      <rect x="22" y="20" width="8" height="26" rx="2" fill="#1D9E75" opacity="0.85" />
      <rect x="36" y="10" width="8" height="36" rx="2" fill="#1D9E75" opacity="0.7" />
      <polyline points="12,28 26,16 40,8" stroke="#1D9E75" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.5" />
    </svg>
  );
}

export default function ChatThread({ messages, onSuggest }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div
      className="flex flex-1 flex-col overflow-y-auto"
      style={{ background: "var(--bg-primary)" }}
    >
      {messages.length === 0 ? (
        /* ── Welcome / empty state ─────────────────────────── */
        <div className="flex flex-1 flex-col items-center justify-center px-4 py-12">
          {/* Glowing hero icon */}
          <div
            className="hero-glow mb-8 flex items-center justify-center rounded-full"
            style={{
              width: 100,
              height: 100,
              background: "radial-gradient(circle at 50% 50%, rgba(29,158,117,0.18) 0%, rgba(29,158,117,0.06) 60%, transparent 100%)",
              border: "1px solid rgba(29,158,117,0.2)",
            }}
          >
            <div
              className="flex items-center justify-center rounded-full"
              style={{
                width: 72,
                height: 72,
                background: "rgba(29,158,117,0.12)",
                border: "1px solid rgba(29,158,117,0.25)",
              }}
            >
              <HeroIcon />
            </div>
          </div>

          {/* Heading */}
          <h1
            className="mb-2 text-center text-2xl font-bold tracking-tight"
            style={{ color: "var(--text-primary)" }}
          >
            Hi! I&apos;m your{" "}
            <span style={{ color: "var(--brand)" }}>BI Agent</span>
          </h1>
          <p
            className="mb-10 max-w-sm text-center text-sm leading-relaxed"
            style={{ color: "var(--text-secondary)" }}
          >
            Ask anything about your data. I&apos;ll help you explore, analyze
            and visualize insights.
          </p>

          {/* Suggestion cards */}
          <div className="grid w-full max-w-lg grid-cols-2 gap-3">
            {SUGGESTIONS.map(({ label, icon }) => (
              <button
                key={label}
                type="button"
                onClick={() => onSuggest(label)}
                className="flex items-center gap-3 rounded-xl px-4 py-3 text-left text-sm font-medium"
                style={{
                  background: "var(--bg-card)",
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                  transition: "all 0.18s ease",
                  boxShadow: "var(--shadow-card)",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = "rgba(29,158,117,0.45)";
                  e.currentTarget.style.background = "var(--bg-hover)";
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.boxShadow = "0 4px 16px rgba(29,158,117,0.12)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "var(--border)";
                  e.currentTarget.style.background = "var(--bg-card)";
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "var(--shadow-card)";
                }}
              >
                <span
                  className="flex shrink-0 items-center justify-center rounded-lg"
                  style={{
                    width: 34, height: 34,
                    background: "rgba(29,158,117,0.12)",
                    color: "var(--brand)",
                  }}
                >
                  {icon}
                </span>
                <span className="leading-snug">{label}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        /* ── Message thread ──────────────────────────────────── */
        <div className="flex flex-col gap-1 px-4 py-5">
          {messages.map((message) => (
            <div key={message.id} className="msg-appear">
              <ChatBubble message={message} />
            </div>
          ))}
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}
