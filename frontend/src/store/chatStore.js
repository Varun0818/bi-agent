import { create } from "zustand";
import { v4 as uuidv4 } from "uuid";

export const useChatStore = create((set) => ({
  messages: [],
  isLoading: false,
  currentSessionId: null,
  error: null,

  addMessage: (role, content, result = null) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: uuidv4(),
          role,
          content,
          result,
          timestamp: Date.now(),
        },
      ],
    })),

  setLoading: (bool) => set({ isLoading: bool }),
  setSessionId: (id) => set({ currentSessionId: id }),
  setError: (msg) => set({ error: msg }),
  clearMessages: () => set({ messages: [] }),

  restoreMessages: (messagesArray) =>
    set({
      messages: messagesArray.map((m) => ({
        id: uuidv4(),
        role: m.role,
        content: m.content,
        result: m.result || null,
        timestamp: m.created_at ? new Date(m.created_at).getTime() : Date.now(),
        isRestored: !m.result,
      })),
    }),
}));
