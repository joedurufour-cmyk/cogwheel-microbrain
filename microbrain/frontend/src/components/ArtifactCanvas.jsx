import { useState } from "react";

export default function ArtifactCanvas({ artifact, compiledDomain, apiBase }) {
  const [copied, setCopied] = useState(false);

  if (!artifact || artifact.status !== "DONE_WITH_ARTIFACT") return null;

  const { canvas, file, output_type } = artifact;
  const score = compiledDomain?.contract_score;

  function handleCopy() {
    navigator.clipboard.writeText(canvas).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    });
  }

  return (
    <section className="artifact-canvas" aria-label="Artifact Output">
      <div className="artifact-header">
        <span className="artifact-label">CANVAS</span>
        <span className="artifact-type">{output_type}</span>
        <div style={{ flex: 1 }} />
        <button className="artifact-copy-btn" onClick={handleCopy}>
          {copied ? "✓ copiado" : "copiar"}
        </button>
        {file?.download_url && (
          <a
            className="artifact-download-btn"
            href={`${apiBase || ""}${file.download_url}`}
            download={file.filename}
          >
            ↓ {file.filename}
          </a>
        )}
      </div>

      <pre className="artifact-content">{canvas}</pre>

      <details className="artifact-debug">
        <summary>debug</summary>
        <div className="artifact-debug-grid">
          <span>domain</span>
          <span>{compiledDomain?.output_envelope?.domain_id || "—"}</span>
          <span>output_type</span>
          <span>{output_type}</span>
          <span>contract</span>
          <span style={{ color: score?.score >= 80 ? "#22d3ee" : "#f59e0b" }}>
            {score != null ? `${score.score}% ${score.contract_complete ? "✓" : "incomplete"}` : "—"}
          </span>
          <span>file</span>
          <span>{file?.filename || "—"}</span>
        </div>
      </details>
    </section>
  );
}
