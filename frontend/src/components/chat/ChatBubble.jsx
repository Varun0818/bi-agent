import ResultCard from "../results/ResultCard";

export default function ChatBubble({ message }) {
  const { role, content, result, timestamp } = message;
  const isUser = role === "user";

  const formatTimestamp = (ts) =>
    new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const hasRealResult =
    result &&
    (result.row_count > 0 ||
      result.error_message ||
      result.generated_sql ||
      (result.insights && result.insights.summary));
  const showResultCard = hasRealResult;

  // Loading skeleton: assistant message with no content yet
  if (!isUser && !content) {
    return (
      <div className="flex justify-start mb-4">
        <div
          className="rounded-xl px-4 py-3"
          style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border)",
            boxShadow: "var(--shadow-card)",
          }}
        >
          <div className="flex gap-1.5 items-center py-1">
            <span
              className="w-2 h-2 rounded-full animate-bounce"
              style={{ background: "var(--brand)", animationDelay: "0ms" }}
            />
            <span
              className="w-2 h-2 rounded-full animate-bounce"
              style={{ background: "var(--brand)", animationDelay: "150ms" }}
            />
            <span
              className="w-2 h-2 rounded-full animate-bounce"
              style={{ background: "var(--brand)", animationDelay: "300ms" }}
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className="max-w-[75%] rounded-xl px-4 py-3"
        style={
          isUser
            ? {
                background: "var(--brand)",
                color: "#fff",
                boxShadow: "var(--shadow-card)",
              }
            : {
                background: "var(--bg-card)",
                color: "var(--text-primary)",
                border: "1px solid var(--border)",
                boxShadow: "var(--shadow-card)",
              }
        }
      >
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{content}</p>

        {!isUser && showResultCard && <ResultCard result={result} />}

        <p
          className="mt-1.5 text-right text-xs"
          style={{ color: isUser ? "rgba(255,255,255,0.65)" : "var(--text-muted)" }}
        >
          {formatTimestamp(timestamp)}
        </p>
      </div>
    </div>
  );
}
