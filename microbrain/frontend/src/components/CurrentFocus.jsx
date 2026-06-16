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
          <strong style={{
            color: ["OUTPUT_RENDERED", "DONE"].includes(
              lastTurn?.domain_state?.next_action_prompt || lastTurn?.llm_dst?.next_move
            ) ? "#22d3ee" : undefined
          }}>
            {(() => {
              const raw = lastTurn?.domain_state?.next_action_prompt ||
                lastTurn?.llm_dst?.next_move ||
                lastTurn?.implication_engine?.next_best_move;
              if (raw === "OUTPUT_RENDERED" || raw === "DONE") return "✓ output compilado";
              return raw ||
                narrative?.open_loops?.[0] ||
                (narrative?.central_objects?.[0] ? "define object input/output contract" : "define system objective");
            })()}
          </strong>
        </div>
        {lastTurn?.compiled_domain?.contract_score != null && (
          <div>
            <span>Contract</span>
            <strong style={{ color: lastTurn.compiled_domain.contract_score.score >= 80 ? "#22d3ee" : "#f59e0b" }}>
              {lastTurn.compiled_domain.contract_score.score}% {lastTurn.compiled_domain.contract_score.contract_complete ? "✓" : "incomplete"}
            </strong>
          </div>
        )}
        <div>
          <span>Connection</span>
          <strong>{statusLabel}</strong>
        </div>
      </div>
    </section>
  );
}
