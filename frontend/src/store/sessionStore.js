import { create } from "zustand";

export const useSessionStore = create((set) => ({
  sessions: [],
  currentSession: null,
  activeSessionId: null,
  sidebarCollapsed: false,

  setSessions: (list) => set({ sessions: list }),
  setCurrentSession: (s) => set({ currentSession: s }),
  setActiveSessionId: (id) => set({ activeSessionId: id }),
  setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),

  addSession: (session) =>
    set((state) => {
      const exists = state.sessions.find(
        (s) => s.session_id === session.session_id
      );
      if (exists) return state;
      return { sessions: [session, ...state.sessions] };
    }),

  updateSessionName: (sessionId, name) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.session_id === sessionId ? { ...s, session_name: name } : s
      ),
    })),

  removeSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.session_id !== sessionId),
    })),

  deleteSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.session_id !== sessionId),
      activeSessionId:
        state.activeSessionId === sessionId ? null : state.activeSessionId,
    })),

  clearAllSessions: () => set({ sessions: [], activeSessionId: null }),
}));
