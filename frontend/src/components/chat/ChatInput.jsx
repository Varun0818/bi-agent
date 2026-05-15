import { useState, useRef, useEffect } from "react";
import TextareaAutosize from "react-textarea-autosize";

function PaperclipIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

export default function ChatInput({ onSend, disabled }) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef(null);
  const canSend = message.trim().length > 0 && !disabled;

  const handleSend = () => {
    if (canSend) {
      onSend(message);
      setMessage("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    if (textareaRef.current) textareaRef.current.focus();
  }, [disabled]);

  return (
    <div
      className="shrink-0 px-4 py-3"
      style={{
        background: "var(--bg-primary)",
        borderTop: "1px solid var(--border)",
      }}
    >
      <div
        className="flex items-end gap-2 rounded-2xl px-3 py-2"
        style={{
          background: "var(--bg-card)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-card)",
          transition: "border-color 0.2s, box-shadow 0.2s",
        }}
        onFocusCapture={(e) => {
          e.currentTarget.style.borderColor = "rgba(29,158,117,0.5)";
          e.currentTarget.style.boxShadow = "0 0 0 3px rgba(29,158,117,0.08)";
        }}
        onBlurCapture={(e) => {
          e.currentTarget.style.borderColor = "var(--border)";
          e.currentTarget.style.boxShadow = "var(--shadow-card)";
        }}
      >
        {/* Paperclip */}
        <button
          type="button"
          title="Attach file"
          disabled
          className="mb-1 flex shrink-0 items-center justify-center rounded-lg p-1.5"
          style={{ color: "var(--text-muted)", cursor: "default" }}
        >
          <PaperclipIcon />
        </button>

        {/* Textarea */}
        <TextareaAutosize
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          minRows={1}
          maxRows={6}
          disabled={disabled}
          placeholder="Type your message..."
          className="flex-1 resize-none bg-transparent text-sm leading-relaxed outline-none"
          style={{
            color: "var(--text-primary)",
            caretColor: "var(--brand)",
          }}
        />

        {/* Send button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={!canSend}
          className="mb-0.5 flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-semibold text-white"
          style={{
            background: canSend ? "var(--brand)" : "rgba(29,158,117,0.35)",
            transition: "background 0.2s, transform 0.1s, opacity 0.2s",
            cursor: canSend ? "pointer" : "not-allowed",
          }}
          onMouseEnter={(e) => { if (canSend) e.currentTarget.style.opacity = "0.88"; }}
          onMouseLeave={(e) => { e.currentTarget.style.opacity = "1"; }}
          onMouseDown={(e) => { if (canSend) e.currentTarget.style.transform = "scale(0.96)"; }}
          onMouseUp={(e) => { e.currentTarget.style.transform = "scale(1)"; }}
        >
          <SendIcon />
          <span>Send</span>
        </button>
      </div>

      <p className="mt-1.5 text-center text-xs" style={{ color: "var(--text-muted)" }}>
        Press <kbd className="rounded px-1 py-0.5 text-xs" style={{ background: "var(--bg-hover)", border: "1px solid var(--border)" }}>Enter</kbd> to send · <kbd className="rounded px-1 py-0.5 text-xs" style={{ background: "var(--bg-hover)", border: "1px solid var(--border)" }}>Shift+Enter</kbd> for new line
      </p>
    </div>
  );
}
