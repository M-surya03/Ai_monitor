import { IconCPU, IconZap, IconClock, IconCheck, IconCode } from "../Icons";
function StatCard({ icon: Icon, label, value, sub, accent = "var(--accent)", loading }) {

  return (
    <div style={{
      background: "var(--bg-surface)",
      border: "1px solid var(--border-subtle)",
      borderRadius: 10,
      padding: "16px 18px",
      display: "flex",
      flexDirection: "column",
      gap: 10
    }}>

      <div style={{ display: "flex", justifyContent: "space-between" }}>

        <span style={{
          fontSize: 9,
          fontWeight: 700,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: "var(--text-faint)"
        }}>
          {label}
        </span>

        <div style={{
          width: 28,
          height: 28,
          borderRadius: 7,
          background: `${accent}18`,
          border: `1px solid ${accent}33`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: accent
        }}>
          <Icon size={13} />
        </div>

      </div>

      {loading ? (

        <div style={{
          height: 28,
          width: "60%",
          borderRadius: 4,
          background: "var(--bg-elevated)"
        }} />

      ) : (

        <>
          <div style={{
            fontSize: 28,
            fontWeight: 700,
            color: "var(--text-primary)"
          }}>
            {value ?? "—"}
          </div>

          {sub && (
            <div style={{ fontSize: 11, color: "var(--text-faint)" }}>
              {sub}
            </div>
          )}
        </>
      )}

    </div>
  );
}

function WeeklyChart({ data = [], loading }) {

  const maxVal = Math.max(...data.map(d => d.count), 1);

  return (
    <div style={{
      background: "var(--bg-surface)",
      border: "1px solid var(--border-subtle)",
      borderRadius: 10,
      padding: "18px",
      gridColumn: "span 2"
    }}>

      <div style={{
        fontSize: 9,
        fontWeight: 700,
        letterSpacing: "0.1em",
        textTransform: "uppercase",
        color: "var(--text-faint)",
        marginBottom: 16
      }}>
        Submissions — Last 7 Days
      </div>

      <div style={{
        display: "flex",
        gap: 6,
        alignItems: "flex-end",
        height: 80
      }}>

        {data.map((d, i) => (

          <div key={i} style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 4
          }}>

            <span style={{
              fontSize: 9,
              color: d.count > 0 ? "var(--accent)" : "transparent"
            }}>
              {d.count}
            </span>

            <div style={{
              width: "100%",
              height: `${Math.max(6, (d.count / maxVal) * 64)}px`,
              background: d.count > 0
                ? "linear-gradient(180deg, var(--accent), #35ecbf)"
                : "var(--bg-overlay)",
              borderRadius: "4px 4px 0 0"
            }} />

            <span style={{
              fontSize: 9,
              color: "var(--text-faint)"
            }}>
              {d.day}
            </span>

          </div>
        ))}

      </div>

    </div>
  );
}

function HistoryTable({ submissions = [], loading }) {

  const LANG_COLOR = {
    javascript: "var(--amber)",
    python: "var(--teal)",
    java: "var(--red)",
    cpp: "var(--accent)"
  };

  return (
    <div style={{
      background: "var(--bg-surface)",
      border: "1px solid var(--border-subtle)",
      borderRadius: 10,
      overflow: "hidden"
    }}>

      <div style={{
        display: "grid",
        gridTemplateColumns: "2fr 1fr 1fr 1fr 120px",
        padding: "10px 16px",
        borderBottom: "1px solid var(--border-subtle)",
        background: "var(--bg-elevated)"
      }}>

        {["Algorithm","Language","Complexity","Optimized","Submitted"].map(h => (

          <span key={h} style={{
            fontSize: 9,
            fontWeight: 700,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: "var(--text-faint)"
          }}>
            {h}
          </span>

        ))}

      </div>

      {submissions.map((s, i) => (

        <div key={i} style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr 1fr 1fr 120px",
          padding: "11px 16px",
          borderBottom: "1px solid var(--border-subtle)"
        }}>

          <span>{s.algorithmDetected}</span>

          <span style={{
            color: LANG_COLOR[(s.language || "").toLowerCase()] ?? "var(--text-muted)"
          }}>
            {s.language}
          </span>

          <span style={{ color: "var(--red)" }}>
            {s.timeComplexity}
          </span>

          <span style={{ color: "var(--teal)" }}>
            {s.improvedComplexity}
          </span>

          <span>
            {s.createdAt
              ? new Date(s.createdAt).toLocaleDateString()
              : "—"}
          </span>

        </div>
      ))}

    </div>
  );
}
export {
  StatCard,
  WeeklyChart,
  HistoryTable
};