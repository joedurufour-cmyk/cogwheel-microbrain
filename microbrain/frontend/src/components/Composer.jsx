import { useState } from "react";

export default function Composer({ onSend }) {
  const [value, setValue] = useState("");

  function submit() {
    const next = value.trim();
    if (!next) return;
    setValue("");
    onSend(next);
  }

  return (
    <form
      className="composer"
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
    >
      <textarea
        value={value}
        placeholder="Describe el sistema, choque o siguiente paso..."
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
          }
        }}
      />
      <button type="submit" aria-label="Enviar mensaje">
        ➤
      </button>
    </form>
  );
}
