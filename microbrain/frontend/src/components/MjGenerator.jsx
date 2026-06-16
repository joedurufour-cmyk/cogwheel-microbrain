import { useState } from "react";

const ENHANCERS = [
  "cinematic composition",
  "high visual clarity",
  "detailed subject",
  "dramatic lighting",
  "rich atmosphere",
  "professional render",
];

const DEFAULT_NEGATIVE =
  "blurry, low quality, distorted, watermark, text overlay, oversaturated, bad anatomy, cropped, out of frame";

const AR_OPTIONS = ["1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "4:5", "5:4", "5:11", "21:9", "7:4"];

function compileLocally(inputText, params) {
  const base = inputText.trim();
  if (!base) return null;
  const suffix = `--ar ${params.ar} --s ${params.s} --c ${params.c} --w ${params.w} --q ${params.q} --v 8.1`;
  const positive = `${base}, ${ENHANCERS.join(", ")} ${suffix}`;
  const negative = params.output_mode === "prompt_plus_negative" ? DEFAULT_NEGATIVE : "";
  const canvas = negative
    ? `POSITIVE PROMPT\n${positive}\n\nNEGATIVE PROMPT\n${negative}`
    : positive;
  return { status: "DONE_WITH_PROMPT", positive_prompt: positive, negative_prompt: negative, canvas, file: null };
}

export default function MjGenerator({ apiBase }) {
  const [inputText, setInputText] = useState("");
  const [params, setParams] = useState({ ar: "1:1", s: 100, c: 0, w: 0, q: 1, output_mode: "prompt_plus_negative" });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copiedPos, setCopiedPos] = useState(false);
  const [copiedAll, setCopiedAll] = useState(false);

  function setParam(key, value) {
    setParams((p) => ({ ...p, [key]: value }));
  }

  async function handleGenerate() {
    if (!inputText.trim()) return;
    setLoading(true);
    setError(null);
    if (!apiBase) {
      setResult(compileLocally(inputText, params));
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${apiBase}/api/mj81/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_text: inputText, params }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch {
      // Fallback to local compile
      setResult(compileLocally(inputText, params));
    } finally {
      setLoading(false);
    }
  }

  function copy(text, setter) {
    navigator.clipboard.writeText(text).then(() => {
      setter(true);
      setTimeout(() => setter(false), 1800);
    });
  }

  const isReady = result?.status === "DONE_WITH_PROMPT";

  return (
    <div className="mj-generator">
      {/* Input zone */}
      <div className="mj-input-zone">
        <textarea
          className="mj-textarea"
          placeholder="Describe la escena que quieres visualizar..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleGenerate();
          }}
        />

        <div className="mj-controls">
          <label className="mj-control">
            <span>AR</span>
            <select value={params.ar} onChange={(e) => setParam("ar", e.target.value)}>
              {AR_OPTIONS.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
          </label>
          <label className="mj-control">
            <span>S</span>
            <input type="number" min="0" max="1000" value={params.s} onChange={(e) => setParam("s", Number(e.target.value))} />
          </label>
          <label className="mj-control">
            <span>C</span>
            <input type="number" min="0" max="100" value={params.c} onChange={(e) => setParam("c", Number(e.target.value))} />
          </label>
          <label className="mj-control">
            <span>W</span>
            <input type="number" min="0" max="3000" value={params.w} onChange={(e) => setParam("w", Number(e.target.value))} />
          </label>
          <label className="mj-control">
            <span>Q</span>
            <select value={params.q} onChange={(e) => setParam("q", Number(e.target.value))}>
              <option value={0.25}>0.25</option>
              <option value={0.5}>0.5</option>
              <option value={1}>1</option>
            </select>
          </label>
          <label className="mj-control">
            <span>Mode</span>
            <select value={params.output_mode} onChange={(e) => setParam("output_mode", e.target.value)}>
              <option value="prompt_plus_negative">+ negative</option>
              <option value="prompt_only">prompt only</option>
            </select>
          </label>
        </div>

        <button
          className="mj-generate-btn"
          onClick={handleGenerate}
          disabled={loading || !inputText.trim()}
        >
          {loading ? "compiling..." : "Generate →"}
        </button>
      </div>

      {error && <div className="mj-error">{error}</div>}

      {/* Output zone */}
      {isReady && (
        <div className="mj-output-zone">
          <div className="mj-canvas-block">
            <div className="mj-canvas-header">
              <span className="mj-canvas-label">POSITIVE PROMPT</span>
              <button className="mj-copy-btn" onClick={() => copy(result.positive_prompt, setCopiedPos)}>
                {copiedPos ? "✓" : "copy"}
              </button>
            </div>
            <pre className="mj-canvas">{result.positive_prompt}</pre>
          </div>

          {result.negative_prompt && (
            <div className="mj-canvas-block">
              <div className="mj-canvas-header">
                <span className="mj-canvas-label">NEGATIVE PROMPT</span>
              </div>
              <pre className="mj-canvas mj-canvas-neg">{result.negative_prompt}</pre>
            </div>
          )}

          <div className="mj-actions">
            <button className="mj-action-btn" onClick={() => copy(result.canvas, setCopiedAll)}>
              {copiedAll ? "✓ copiado" : "Copy All"}
            </button>
            {result.file?.download_url && (
              <a
                className="mj-action-btn mj-dl"
                href={`${apiBase || ""}${result.file.download_url}`}
                download={result.file.filename}
              >
                ↓ {result.file.filename}
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
