// components/editor/AnalyzeButton.jsx
import { useState } from "react";
import { IconPlay } from "../Icons";

function Spinner() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2.5" style={{ animation: "spin 0.75s linear infinite", flexShrink: 0 }}>
      <circle cx="12" cy="12" r="10" strokeOpacity="0.15" />
      <path d="M12 2a10 10 0 0 1 10 10" />
    </svg>
  );
}

export default function AnalyzeButton({ onClick, loading = false, disabled = false }) {
  const [hovered, setHovered] = useState(false);

  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: "flex", alignItems: "center", gap: 6,
        padding: "6px 14px",
        background: loading
          ? "var(--bg-overlay)"
          : hovered
          ? "var(--accent-hover)"
          : "var(--accent)",
        border: loading ? "1px solid var(--border-default)" : "1px solid transparent",
        borderRadius: 6,
        color: loading ? "var(--text-muted)" : "#fff",
        fontFamily: "var(--font-ui)", fontSize: 12, fontWeight: 600,
        cursor: loading || disabled ? "not-allowed" : "pointer",
        transition: "all 0.15s",
        boxShadow: !loading && hovered ? "var(--accent-glow)" : "none",
        whiteSpace: "nowrap",
        letterSpacing: "0.01em",
      }}
    >
      {loading ? <Spinner /> : <IconPlay size={12} />}
      {loading ? "Analyzing…" : "Run Analysis"}
      {!loading && (
        <kbd style={{
          fontSize: 9, opacity: 0.55, fontWeight: 400,
          background: "rgba(255,255,255,0.12)",
          border: "1px solid rgba(255,255,255,0.15)",
          borderRadius: 3, padding: "1px 4px",
          fontFamily: "var(--font-ui)",
        }}>
          ⌘↵
        </kbd>
      )}
    </button>
  );
}