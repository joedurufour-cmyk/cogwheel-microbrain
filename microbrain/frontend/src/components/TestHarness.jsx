import { useState } from "react";

export default function TestHarness({ apiBase }) {
  const [result, setResult] = useState({ status: "not_run" });

  async function run() {
    const response = await fetch(`${apiBase}/tests/run`, { method: "POST" });
    setResult(await response.json());
  }

  return (
    <>
      <button className="drawer-action" type="button" onClick={run}>
        Run Kernel Tests
      </button>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </>
  );
}
