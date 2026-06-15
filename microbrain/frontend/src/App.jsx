import { useEffect, useState } from "react";
import ChatView from "./components/ChatView.jsx";
import Composer from "./components/Composer.jsx";
import CurrentFocus from "./components/CurrentFocus.jsx";
import DevDrawer from "./components/DevDrawer.jsx";
import Header from "./components/Header.jsx";

const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? "http://localhost:8000" : "");

const LOCAL_NARRATIVE = {
  objective: null,
  active_problem: null,
  current_hypothesis: null,
  current_architecture: [],
  current_risks: [],
  open_loops: [],
  decisions: [],
  validations: []
};

function inferLocalTurn(rawInput, previousNarrative = LOCAL_NARRATIVE) {
  const text = rawInput.toLowerCase();
  const isBuild = /constru|crear|hacer|c[oó]digo|deploy|netlify|github|backend|frontend|prompt|midjourney|v8/.test(text);
  const isValidation = /valid|probar|test|funciona|sirve|medir/.test(text);
  const isBroken = /no|falta|error|fall|jodido|blanco|problema|bloque/.test(text);
  const isScope = /y|adem[aá]s|todo|par[aá]metros|reordene|generador/.test(text) && rawInput.length > 80;

  const objective =
    previousNarrative?.objective ||
    (isBuild ? "construir un sistema vertical operativo" : "definir el sistema");
  const activeProblem = isBroken
    ? "hay una brecha entre interfaz desplegada y motor operativo"
    : isScope
      ? "la solicitud mezcla alcance, contrato y salida esperada"
      : "falta congelar el siguiente movimiento";
  const collisionType = isBroken
    ? "contract_violation"
    : isScope
      ? "scope_explosion"
      : isValidation
        ? "design_without_validation"
        : "missing_context";
  const nextBestMove = isBuild
    ? "congelar el contrato de entrada/salida antes de agregar mas funciones"
    : isValidation
      ? "definir casos de prueba medibles"
      : "formular el objetivo en una frase verificable";

  const narrative = {
    ...previousNarrative,
    objective,
    active_problem: activeProblem,
    current_risks: Array.from(new Set([...(previousNarrative?.current_risks || []), collisionType])),
    open_loops: Array.from(new Set([nextBestMove, ...(previousNarrative?.open_loops || [])])).slice(0, 5)
  };

  const turn = {
    raw_input: rawInput,
    user_narrative: {
      stated_goal: isBuild ? rawInput : null,
      stated_problem: isBroken ? rawInput : null,
      stated_constraints: [],
      stated_beliefs: [],
      emotional_signal: isBroken ? "friction" : "neutral"
    },
    inferred_narrative: {
      inferred_goal: objective,
      inferred_problem: activeProblem,
      inferred_constraints: ["sin backend publico conectado"],
      inferred_beliefs: [],
      inferred_risk: collisionType
    },
    collision_detection: {
      exists: true,
      type: collisionType,
      severity: isBroken ? 0.82 : 0.64,
      evidence: [rawInput]
    },
    implication_engine: {
      implications: ["el sistema debe responder aun sin completar infraestructura externa"],
      risks: [collisionType],
      next_best_move: nextBestMove
    },
    response_plan: {
      move: isBroken ? "correct" : isValidation ? "test" : "decompose",
      purpose: "mantener avance operativo sin perder contrato del sistema",
      must_include: ["colision detectada", "narrativa actual", "siguiente movimiento"],
      must_avoid: ["respuesta generica", "debug visible"]
    },
    answer: [
      `Detecto una colision: ${collisionType}.`,
      "",
      "Narrativa actual:",
      `- objetivo: ${objective}`,
      `- problema activo: ${activeProblem}`,
      `- riesgo: avanzar sin cerrar ${collisionType}`,
      "",
      `Siguiente movimiento: ${nextBestMove}.`
    ].join("\n")
  };

  return { turn, narrative };
}

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
      setApiStatus("local");
      setNarrative(LOCAL_NARRATIVE);
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
      setNarrative(LOCAL_NARRATIVE);
      setMessages((items) => [
        ...items,
        {
          role: "bot",
          text: "Backend no conectado. Activo motor local temporal para mantener el flujo hasta conectar VITE_API_BASE."
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
      const { turn, narrative: nextNarrative } = inferLocalTurn(rawInput, narrative || LOCAL_NARRATIVE);
      setLastTurn(turn);
      setNarrative(nextNarrative);
      setApiStatus("local");
      setMessages((items) => [...items, { role: "bot", text: turn.answer }]);
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
      const { turn, narrative: nextNarrative } = inferLocalTurn(rawInput, narrative || LOCAL_NARRATIVE);
      setLastTurn(turn);
      setNarrative(nextNarrative);
      setMessages((items) => [
        ...items,
        { role: "bot", text: turn.answer }
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
