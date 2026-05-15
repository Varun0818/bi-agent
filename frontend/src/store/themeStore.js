import { create } from "zustand";

const STORAGE_KEY = "bi-agent-theme";

export const useThemeStore = create((set, get) => ({
  theme: localStorage.getItem(STORAGE_KEY) || "light",

  toggleTheme: () => {
    const next = get().theme === "light" ? "dark" : "light";
    localStorage.setItem(STORAGE_KEY, next);
    document.documentElement.setAttribute("data-theme", next);
    set({ theme: next });
  },
}));
