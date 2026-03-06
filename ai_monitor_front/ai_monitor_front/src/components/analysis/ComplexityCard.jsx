// components/analysis/ComplexityCard.jsx
import { IconArrowRight, IconClock } from "../Icons";
import { COMPLEXITY_COLOR, COMPLEXITY_BG, COMPLEXITY_BORDER } from "../../theme";

function Badge({ value }) {
  if (!value) return <span style={{ color: "var(--text-faint)" }}>—</span>;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      padding: "3px 9px",
      background: COMPLEXITY_BG(value),
      border: `1px solid ${COMPLEXITY_BORDER(value)}`,
      borderRadius: 5,
      fontFamily: "var(--font-code)", fontSize: 12, fontWeight: 700,
      color: COMPLEXITY_COLOR(value),
      letterSpacing: "0.04em",
    }}>
      {value}
    </span>
  );
}

export default function ComplexityCard({ before, after }) {
  return (
    <div style={{
      background: "var(--bg-surface)",
      border: "1px solid var(--border-subtle)",
      borderRadius: 8,
      padding: 12,
    }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 5,
        marginBottom: 10,
      }}>
        <IconClock size={11} style={{ color: "var(--text-muted)" }} />
        <span style={{
          fontSize: 9, fontWeight: 700,
          letterSpacing: "0.1em", textTransform: "uppercase",
          color: "var(--text-muted)",
        }}>
          Time Complexity
        </span>
      </div>

      <div style={{
        display: "flex", alignItems: "center", gap: 10,
      }}>
        <Badge value={before} />

        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{
            height: 1, flex: 1,
            background: "linear-gradient(90deg, var(--red-border), transparent)",
          }} />
          <span style={{ padding: "0 6px", color: "var(--text-faint)" }}>
            <IconArrowRight size={12} />
          </span>
          <div style={{
            height: 1, flex: 1,
            background: "linear-gradient(90deg, transparent, var(--teal-border))",
          }} />
        </div>

        <Badge value={after} />
      </div>

      {/* Improvement pill */}
      {before && after && before !== after && (
        <div style={{
          marginTop: 8, textAlign: "center",
          fontSize: 10, color: "var(--teal)",
          fontFamily: "var(--font-code)",
        }}>
          Complexity reduced
        </div>
      )}
    </div>
  );
}