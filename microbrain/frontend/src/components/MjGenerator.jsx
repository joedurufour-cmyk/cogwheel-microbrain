import { useState, useEffect } from "react";
import { Check, Copy, Download, Zap } from "lucide-react";
import { compilePlatformPrompt } from "@/lib/platformCompilers";

const PLATFORMS = [
  { id: "midjourney_v8_1", label: "Midjourney V8.1" },
  { id: "dalle_3", label: "DALL·E 3" },
  { id: "nano_banana", label: "Nano Banana" },
];

const AR_OPTIONS = ["1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4", "4:5", "5:4", "5:11", "21:9", "7:4"];

export default function MjGenerator({ apiBase }) {
  const [inputText, setInputText] = useState("");
  const [platform, setPlatform] = useState("midjourney_v8_1");
  const [params, setParams] = useState({ ar: "1:1", s: 100, c: 0, w: 0, q: 1, output_mode: "prompt_plus_negative" });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copiedPos, setCopiedPos] = useState(false);
  const [copiedAll, setCopiedAll] = useState(false);

  // Clear stale result when user edits input
  useEffect(() => {
    setResult(null);
    setError(null);
  }, [inputText]);

  // Reset output_mode when switching platforms (DALL·E / Nano Banana have no negative)
  useEffect(() => {
    setParams((p) => ({
      ...p,
      output_mode: platform === "midjourney_v8_1" ? "prompt_plus_negative" : "prompt_only",
    }));
  }, [platform]);

  function setParam(key, value) {
    setParams((p) => ({ ...p, [key]: value }));
  }

  async function handleGenerate() {
    if (!inputText.trim()) return;
    setResult(null);
    setError(null);
    setLoading(true);
    const fullParams = { ...params, platform };
    if (!apiBase) {
      setResult(compilePlatformPrompt(inputText, platform, fullParams));
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`${apiBase}/api/mj81/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_text: inputText, params: fullParams }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch {
      setResult(compilePlatformPrompt(inputText, platform, fullParams));
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

  const isMj = platform === "midjourney_v8_1";
  const isReady = result?.status === "DONE_WITH_PROMPT";

  return (
    <div className="mj-generator">
      {/* Platform selector */}
      <div className="mj-platform-bar">
        {PLATFORMS.map((p) => (
          <button
            key={p.id}
            type="button"
            className={`mj-platform-btn${platform === p.id ? " active" : ""}`}
            onClick={() => setPlatform(p.id)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Input zone */}
      <div className="mj-input-zone">
        <textarea
          className="mj-textarea"
          placeholder="Describe tu imagen..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleGenerate();
          }}
        />

        {isMj && (
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
        )}

        <button
          className="mj-generate-btn"
          onClick={handleGenerate}
          disabled={loading || !inputText.trim()}
        >
          {loading ? "compiling…" : <><Zap size={15} />Generate</>}
        </button>
      </div>

      {error && <div className="mj-error">{error}</div>}

      {/* Output zone */}
      {isReady && (
        <div className="mj-output-zone">
          <div className="mj-section-label">Generated Prompt</div>

          <div className="mj-canvas-block">
            <div className="mj-canvas-header">
              <span className="mj-canvas-label">POSITIVE PROMPT</span>
              <button className="mj-copy-btn" onClick={() => copy(result.positive_prompt, setCopiedPos)}>
                {copiedPos ? <Check size={12} /> : <Copy size={12} />}
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
              {copiedAll ? <><Check size={13} />Copiado</> : <><Copy size={13} />Copy All</>}
            </button>
            {result.file?.download_url && (
              <a
                className="mj-action-btn mj-dl"
                href={`${apiBase || ""}${result.file.download_url}`}
                download={result.file.filename}
              >
                <Download size={13} />{result.file.filename}
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
