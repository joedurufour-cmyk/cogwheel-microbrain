import { useEffect, useState } from "react";
import ChatView from "./components/ChatView.jsx";
import Composer from "./components/Composer.jsx";
import CurrentFocus from "./components/CurrentFocus.jsx";
import DevDrawer from "./components/DevDrawer.jsx";
import Header from "./components/Header.jsx";

const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Trae el sistema que estas construyendo. Voy a cuidar objetivo, contrato, riesgo y siguiente movimiento."
    }
  ]);
  const [narrative, setNarrative] = useState(null);
  const [lastTurn, setLastTurn] = useState(null);
  const [developerMode, setDeveloperMode] = useState(false);
  const [apiStatus, setApiStatus] = useState(API_BASE ? "connecting" : "missing");

  useEffect(() => {
    bootstrapSession();
  }, []);

  useEffect(() => {
    const handler = (event) => {
      if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === "d") {
        event.preventDefault();
        setDeveloperMode((value) => !value);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  async function bootstrapSession() {
    if (!API_BASE) {
      setApiStatus("missing");
      return;
    }
    const stored = sessionStorage.getItem("microbrain_session_id");
    if (stored) {
      setSessionId(Number(stored));
      await refreshNarrative(Number(stored));
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "System Design Session" })
      });
      if (!response.ok) throw new Error(`Session request failed: ${response.status}`);
      const session = await response.json();
      sessionStorage.setItem("microbrain_session_id", String(session.id));
      setSessionId(session.id);
      setApiStatus("ready");
      await refreshNarrative(session.id);
    } catch (error) {
      setApiStatus("unreachable");
      setMessages((items) => [
        ...items,
        {
          role: "bot",
          text: "Backend no conectado. La interfaz esta lista; configura VITE_API_BASE con la URL publica del API para procesar turnos."
        }
      ]);
    }
  }

  async function refreshNarrative(id = sessionId) {
    if (!API_BASE || !id) return;
    try {
      const response = await fetch(`${API_BASE}/sessions/${id}/narrative`);
      if (!response.ok) throw new Error(`Narrative request failed: ${response.status}`);
      setNarrative(await response.json());
      setApiStatus("ready");
    } catch {
      setApiStatus("unreachable");
    }
  }

  async function sendTurn(rawInput) {
    setMessages((items) => [...items, { role: "user", text: rawInput }]);
    if (!API_BASE || !sessionId) {
      setMessages((items) => [
        ...items,
        {
          role: "bot",
          text: "No puedo procesar el turno todavia: falta conectar el backend publico en VITE_API_BASE."
        }
      ]);
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/turns`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_input: rawInput })
      });
      if (!response.ok) throw new Error(`Turn request failed: ${response.status}`);
      const turn = await response.json();
      setLastTurn(turn);
      setMessages((items) => [...items, { role: "bot", text: turn.answer }]);
      await refreshNarrative(sessionId);
    } catch {
      setApiStatus("unreachable");
      setMessages((items) => [
        ...items,
        {
          role: "bot",
          text: "El API no respondio. Revisa que el backend este desplegado y que VITE_API_BASE apunte a su URL HTTPS."
        }
      ]);
    }
  }

  return (
    <>
      <main className="app-shell">
        <Header developerMode={developerMode} onToggleDev={() => setDeveloperMode((value) => !value)} />
        <ChatView messages={messages} />
        <CurrentFocus narrative={narrative} lastTurn={lastTurn} apiStatus={apiStatus} />
        <Composer onSend={sendTurn} />
      </main>
      <DevDrawer
        apiBase={API_BASE}
        sessionId={sessionId}
        open={developerMode}
        onClose={() => setDeveloperMode(false)}
        narrative={narrative}
        lastTurn={lastTurn}
      />
    </>
  );
}
