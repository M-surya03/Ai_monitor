// components/editor/LanguageSelector.jsx
import { useState } from "react";
import { LANGS, LANG_LABELS } from "../../theme";
import { IconChevronDown } from "../Icons";

export default function LanguageSelector({ value, onChange }) {
  const [open, setOpen] = useState(false);

  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          display: "flex", alignItems: "center", gap: 5,
          padding: "4px 8px 4px 10px",
          background: open ? "var(--bg-overlay)" : "var(--bg-surface)",
          border: `1px solid ${open ? "var(--accent-border)" : "var(--border-subtle)"}`,
          borderRadius: 5,
          color: "var(--text-secondary)",
          fontFamily: "var(--font-code)", fontSize: 11, fontWeight: 500,
          cursor: "pointer",
          transition: "all 0.15s",
          whiteSpace: "nowrap",
        }}
      >
        <span style={{
          width: 7, height: 7, borderRadius: "50%",
          background: "var(--accent)", flexShrink: 0,
        }} />
        {LANG_LABELS[value] ?? value}
        <IconChevronDown size={11} style={{
          transform: open ? "rotate(180deg)" : "rotate(0deg)",
          transition: "transform 0.15s",
          color: "var(--text-faint)",
        }} />
      </button>

      {open && (
        <div style={{
          position: "absolute", top: "calc(100% + 4px)", left: 0,
          background: "var(--bg-elevated)",
          border: "1px solid var(--border-default)",
          borderRadius: 6,
          overflow: "hidden",
          zIndex: 50,
          minWidth: 140,
          boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
          animation: "fade-up 0.15s ease",
        }}>
          {LANGS.map((l) => (
            <button
              key={l}
              onClick={() => { onChange(l); setOpen(false); }}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                width: "100%", padding: "7px 12px",
                background: value === l ? "var(--accent-dim)" : "transparent",
                border: "none",
                color: value === l ? "var(--accent)" : "var(--text-secondary)",
                fontFamily: "var(--font-code)", fontSize: 11,
                cursor: "pointer",
                textAlign: "left",
                transition: "background 0.1s",
              }}
              onMouseEnter={(e) => {
                if (value !== l) e.currentTarget.style.background = "var(--bg-overlay)";
              }}
              onMouseLeave={(e) => {
                if (value !== l) e.currentTarget.style.background = "transparent";
              }}
            >
              {value === l && (
                <span style={{ width: 4, height: 4, borderRadius: "50%", background: "var(--accent)" }} />
              )}
              {value !== l && <span style={{ width: 4 }} />}
              {LANG_LABELS[l]}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}