export default function CurrentFocus({ narrative, lastTurn, apiStatus }) {
  const statusLabel = {
    ready: "api connected",
    connecting: "connecting api",
    missing: "api not configured",
    unreachable: "api unreachable"
  }[apiStatus] || "api not configured";

  return (
    <section className="focus-card" aria-label="Current Focus">
      <div className="focus-card-head">Current Focus</div>
      <div className="focus-grid">
        <div>
          <span>Objective</span>
          <strong>{narrative?.objective || "none"}</strong>
        </div>
        <div>
          <span>Active Problem</span>
          <strong>{narrative?.active_problem || "none"}</strong>
        </div>
        <div>
          <span>Next Move</span>
          <strong>{lastTurn?.implication_engine?.next_best_move || narrative?.open_loops?.[0] || "define system objective"}</strong>
        </div>
        <div>
          <span>Connection</span>
          <strong>{statusLabel}</strong>
        </div>
      </div>
    </section>
  );
}
