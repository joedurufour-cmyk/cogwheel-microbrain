export default function CurrentFocus({ narrative, lastTurn, apiStatus }) {
  const statusLabel = {
    ready: "api connected",
    connecting: "connecting api",
    local: "local engine",
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
          <span>Central Object</span>
          <strong>{narrative?.central_objects?.[0] || "none"}</strong>
        </div>
        <div>
          <span>Active Domain</span>
          <strong>{narrative?.active_domain || lastTurn?.domain_state?.active_domain || "none"}</strong>
        </div>
        <div>
          <span>Blocking Gap</span>
          <strong>{narrative?.blocking_gap || "none"}</strong>
        </div>
        <div>
          <span>Next Move</span>
          <strong>
            {lastTurn?.llm_dst?.next_move ||
              lastTurn?.domain_state?.next_action_prompt ||
              lastTurn?.implication_engine?.next_best_move ||
              narrative?.open_loops?.[0] ||
              (narrative?.central_objects?.[0] ? "define object input/output contract" : "define system objective")}
          </strong>
        </div>
        <div>
          <span>Connection</span>
          <strong>{statusLabel}</strong>
        </div>
      </div>
    </section>
  );
}
