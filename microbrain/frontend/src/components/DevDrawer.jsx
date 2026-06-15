import { useState } from "react";
import TestHarness from "./TestHarness.jsx";

export default function DevDrawer({ apiBase, sessionId, open, onClose, narrative, lastTurn }) {
  const [exportJson, setExportJson] = useState(null);

  async function exportSession() {
    if (!sessionId) return;
    const response = await fetch(`${apiBase}/sessions/${sessionId}/export`);
    setExportJson(await response.json());
  }

  return (
    <aside className={`developer-drawer ${open ? "open" : ""}`} aria-hidden={!open}>
      <div className="drawer-header">
        <div>
          <h2>Developer Mode</h2>
          <p>Turn report, narrative memory, collision and implication engine.</p>
        </div>
        <button className="icon-button" type="button" onClick={onClose}>
          x
        </button>
      </div>
      <details open>
        <summary>Turn Report</summary>
        <pre>{JSON.stringify(lastTurn?.report || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Narrative State</summary>
        <pre>{JSON.stringify(narrative || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Collision Detection</summary>
        <pre>{JSON.stringify(lastTurn?.collision_detection || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Implication Engine</summary>
        <pre>{JSON.stringify(lastTurn?.implication_engine || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Extracted Objects</summary>
        <pre>{JSON.stringify(lastTurn?.object_extraction || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Relation Triples</summary>
        <pre>{JSON.stringify(lastTurn?.relationship_graph?.active_relations || [], null, 2)}</pre>
      </details>
      <details>
        <summary>Canonical Aliases</summary>
        <pre>{JSON.stringify(lastTurn?.object_extraction?.aliases || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Gaps</summary>
        <pre>{JSON.stringify(lastTurn?.relationship_graph?.gaps || [], null, 2)}</pre>
      </details>
      <details>
        <summary>Graph JSON</summary>
        <pre>{JSON.stringify(lastTurn?.relationship_graph?.graph_json || narrative?.object_graph || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Raw JSON</summary>
        <pre>{JSON.stringify(lastTurn || {}, null, 2)}</pre>
      </details>
      <details>
        <summary>Test Harness</summary>
        <TestHarness apiBase={apiBase} />
      </details>
      <details>
        <summary>Export Session JSON</summary>
        <button className="drawer-action" type="button" onClick={exportSession}>
          Export Session JSON
        </button>
        <pre>{JSON.stringify(exportJson || {}, null, 2)}</pre>
      </details>
    </aside>
  );
}
