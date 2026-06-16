import { useEffect, useRef } from "react";

function renderBlock(text) {
  const parts = [];
  const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
  let last = 0;
  let match;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    if (match.index > last) {
      parts.push({ type: "text", content: text.slice(last, match.index) });
    }
    parts.push({ type: "code", lang: match[1] || "text", content: match[2].trim() });
    last = match.index + match[0].length;
  }
  if (last < text.length) {
    parts.push({ type: "text", content: text.slice(last) });
  }
  return parts;
}

function CsvTable({ content }) {
  const rows = content.trim().split("\n").map(r => r.split(","));
  if (rows.length < 2) return <pre className="code-block">{content}</pre>;
  const [headers, ...body] = rows;
  return (
    <div className="csv-table-wrap">
      <table className="csv-table">
        <thead>
          <tr>{headers.map((h, i) => <th key={i}>{h.trim()}</th>)}</tr>
        </thead>
        <tbody>
          {body.map((row, ri) => (
            <tr key={ri}>{row.map((cell, ci) => <td key={ci}>{cell.trim()}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MessageContent({ text }) {
  const parts = renderBlock(text);
  return (
    <>
      {parts.map((part, i) => {
        if (part.type === "code") {
          if (part.lang === "csv") return <CsvTable key={i} content={part.content} />;
          return (
            <div key={i} className="code-block-wrap">
              {part.lang && part.lang !== "text" && (
                <span className="code-lang">{part.lang}</span>
              )}
              <pre className="code-block"><code>{part.content}</code></pre>
            </div>
          );
        }
        return (
          <p key={i} className="bubble-text">
            {part.content.split("\n").map((line, li) => (
              <span key={li}>
                {line.startsWith("# ") ? <strong className="heading-1">{line.slice(2)}</strong>
                  : line.startsWith("## ") ? <strong className="heading-2">{line.slice(3)}</strong>
                  : line.startsWith("**") && line.endsWith("**") ? <strong>{line.slice(2, -2)}</strong>
                  : line}
                {li < part.content.split("\n").length - 1 && <br />}
              </span>
            ))}
          </p>
        );
      })}
    </>
  );
}

export default function ChatView({ messages }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [messages]);

  return (
    <section ref={ref} className="chat-log" aria-label="Conversacion">
      {messages.map((message, index) => (
        <article key={`${message.role}-${index}`} className={`bubble ${message.role === "user" ? "user" : "bot"}`}>
          {message.role === "user"
            ? <p>{message.text}</p>
            : <MessageContent text={message.text} />
          }
        </article>
      ))}
    </section>
  );
}
