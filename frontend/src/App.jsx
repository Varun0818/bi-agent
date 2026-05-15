import { useEffect } from "react";
import ChatPage from "./pages/ChatPage";
import { useThemeStore } from "./store/themeStore";

export default function App() {
  const theme = useThemeStore((s) => s.theme);

  useEffect(() => {
    const saved = localStorage.getItem("bi-agent-theme") || "light";
    document.documentElement.setAttribute("data-theme", saved);
  }, []);

  return (
    <div data-theme={theme}>
      <ChatPage />
    </div>
  );
}
