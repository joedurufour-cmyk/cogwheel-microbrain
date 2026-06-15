export default function Header({ onToggleDev }) {
  return (
    <header className="brand-header">
      <div className="emblem-wrap" aria-hidden="true">
        <svg className="emblem" viewBox="0 0 96 96">
          <path
            fill="rgba(34, 211, 238, 0.16)"
            stroke="#22d3ee"
            strokeWidth="3"
            strokeLinejoin="round"
            d="M48 10l5.5 10.8c2.7.5 5.3 1.3 7.7 2.4l10.5-6.1 7.2 7.2-6.1 10.5c1.1 2.4 1.9 5 2.4 7.7L86 48l-10.8 5.5a28.2 28.2 0 0 1-2.4 7.7l6.1 10.5-7.2 7.2-10.5-6.1c-2.4 1.1-5 1.9-7.7 2.4L48 86l-5.5-10.8a28.2 28.2 0 0 1-7.7-2.4l-10.5 6.1-7.2-7.2 6.1-10.5c-1.1-2.4-1.9-5-2.4-7.7L10 48l10.8-5.5c.5-2.7 1.3-5.3 2.4-7.7l-6.1-10.5 7.2-7.2 10.5 6.1c2.4-1.1 5-1.9 7.7-2.4L48 10z"
          />
          <circle cx="48" cy="48" r="20" fill="#070b10" stroke="#9befff" strokeWidth="3" />
          <circle cx="48" cy="48" r="6" fill="#22d3ee" />
        </svg>
      </div>
      <div className="brand-copy">
        <h1>Cogwheel</h1>
        <p>System Design Navigator</p>
      </div>
      <button className="icon-button" type="button" onClick={onToggleDev} aria-label="Developer mode">
        {"</>"}
      </button>
    </header>
  );
}
