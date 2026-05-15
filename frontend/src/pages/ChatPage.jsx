import { useEffect } from "react";
import Sidebar from "../components/layout/Sidebar";
import Header from "../components/layout/Header";
import ChatThread from "../components/chat/ChatThread";
import ChatInput from "../components/chat/ChatInput";
import { useChatStore } from "../store/chatStore";
import { useSessionStore } from "../store/sessionStore";
import {
  sendQuery,
  getSessions,
  getSessionMessages,
  deleteSession,
  clearAllSessions,
  cleanupGarbageSessions,
} from "../api/chatApi";

export default function ChatPage() {
  const messages = useChatStore((s) => s.messages);
  const isLoading = useChatStore((s) => s.isLoading);
  const currentSessionId = useChatStore((s) => s.currentSessionId);
  const addMessage = useChatStore((s) => s.addMessage);
  const setLoading = useChatStore((s) => s.setLoading);
  const setSessionId = useChatStore((s) => s.setSessionId);
  const setError = useChatStore((s) => s.setError);
  const clearMessages = useChatStore((s) => s.clearMessages);
  const restoreMessages = useChatStore((s) => s.restoreMessages);

  const sessions = useSessionStore((s) => s.sessions);
  const setSessions = useSessionStore((s) => s.setSessions);
  const addSession = useSessionStore((s) => s.addSession);
  const activeSessionId = useSessionStore((s) => s.activeSessionId);
  const setActiveSessionId = useSessionStore((s) => s.setActiveSessionId);
  const updateSessionName = useSessionStore((s) => s.updateSessionName);
  const deleteSessionStore = useSessionStore((s) => s.deleteSession);
  const clearAllSessionsStore = useSessionStore((s) => s.clearAllSessions);
  const sidebarCollapsed = useSessionStore((s) => s.sidebarCollapsed);

  useEffect(() => {
    const init = async () => {
      try {
        const data = await getSessions();
        setSessions(data.sessions || data || []);
      } catch (e) {
        console.error("Failed to load sessions", e);
      }
      try {
        await cleanupGarbageSessions();
      } catch {
        // non-critical, ignore
      }
    };
    init();
  }, [setSessions]);

  async function handleSessionClick(session) {
    if (session.session_id === activeSessionId) return;
    try {
      setLoading(true);
      setActiveSessionId(session.session_id);
      setSessionId(session.session_id);
      setError(null);
      const msgs = await getSessionMessages(session.session_id);
      if (msgs && msgs.length > 0) {
        restoreMessages(msgs);
      } else {
        clearMessages();
      }
    } catch (e) {
      console.error("Session load failed:", e);
      clearMessages();
    } finally {
      setLoading(false);
    }
  }

  function handleNewChat() {
    clearMessages();
    setSessionId(null);
    setActiveSessionId(null);
    setError(null);
  }

  async function handleDeleteSession(sessionId) {
    try {
      await deleteSession(sessionId);
      deleteSessionStore(sessionId);
      if (activeSessionId === sessionId) {
        handleNewChat();
      }
    } catch (err) {
      console.error("Delete failed:", err);
    }
  }

  async function handleClearAll() {
    try {
      await clearAllSessions();
      clearAllSessionsStore();
      handleNewChat();
    } catch (err) {
      console.error("Clear all failed:", err);
    }
  }

  async function handleSend(message) {
    addMessage("user", message);
    setLoading(true);
    try {
      const result = await sendQuery(message, currentSessionId);
      addMessage(
        "assistant",
        result.insights?.summary || "Query complete",
        result
      );
      if (result.session_id) {
        setSessionId(result.session_id);
        setActiveSessionId(result.session_id);
        const existingSession = sessions.find(
          (s) => s.session_id === result.session_id
        );
        if (!existingSession) {
          addSession({
            session_id: result.session_id,
            session_name: message.slice(0, 40),
          });
        } else if (existingSession.session_name === "New Chat") {
          updateSessionName(result.session_id, message.slice(0, 40));
        }
      }
    } catch {
      addMessage("assistant", "Something went wrong.", null);
    } finally {
      setLoading(false);
    }
  }

  const sidebarWidth = sidebarCollapsed ? 56 : 256;

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: "var(--bg-primary)" }}>
      <Sidebar
        onSessionClick={handleSessionClick}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onClearAll={handleClearAll}
      />

      <div
        className="flex flex-1 flex-col overflow-hidden transition-all duration-200"
        style={{ marginLeft: sidebarWidth }}
      >
        <Header />

        <div className="flex flex-1 flex-col overflow-hidden">
          <ChatThread messages={messages} onSuggest={handleSend} />
          <ChatInput onSend={handleSend} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
