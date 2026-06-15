import { useEffect, useRef } from "react";

export default function ChatView({ messages }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [messages]);

  return (
    <section ref={ref} className="chat-log" aria-label="Conversacion">
      {messages.map((message, index) => (
        <article key={`${message.role}-${index}`} className={`bubble ${message.role === "user" ? "user" : "bot"}`}>
          <p>{message.text}</p>
        </article>
      ))}
    </section>
  );
}
