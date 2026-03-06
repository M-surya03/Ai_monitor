// components/analysis/AlgorithmCard.jsx  (FIXED)
// Was importing from @mui/material — crashed the entire sidebar silently.
// Now uses the same pure-CSS design as every other component.

import { IconCode, IconZap } from "../Icons";

export default function AlgorithmCard({ detected, suggested }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
      {[
        {
          label:  "Detected",
          value:  detected,
          icon:   IconCode,
          color:  "var(--red)",
          bg:     "var(--red-dim)",
          border: "var(--red-border)",
        },
        {
          label:  "Optimized to",
          value:  suggested,
          icon:   IconZap,
          color:  "var(--teal)",
          bg:     "var(--teal-dim)",
          border: "var(--teal-border)",
        },
      ].map(({ label, value, icon: Icon, color, bg, border }) => (
        <div key={label} style={{
          background: bg,
          border: `1px solid ${border}`,
          borderRadius: 8,
          padding: 12,
        }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 5, marginBottom: 7,
          }}>
            <Icon size={11} style={{ color }} />
            <span style={{
              fontSize: 9, fontWeight: 700,
              letterSpacing: "0.1em", textTransform: "uppercase",
              color,
            }}>
              {label}
            </span>
          </div>
          <div style={{
            fontFamily: "var(--font-code)", fontSize: 11, fontWeight: 600,
            color: "var(--text-primary)", lineHeight: 1.4,
          }}>
            {value ?? "—"}
          </div>
        </div>
      ))}
    </div>
  );
}