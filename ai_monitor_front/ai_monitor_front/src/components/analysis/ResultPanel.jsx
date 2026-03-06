// components/analysis/ResultPanel.jsx

import { useState } from "react";
import { IconTerminal, IconAlert, IconCheck } from "../Icons";

const TABS = [
  { id: "output", label: "Output", icon: IconTerminal },
  { id: "problem", label: "Problem", icon: IconAlert },
];

export default function ResultPanel({ result, loading, onRunOptimized }) {

  const [tab, setTab] = useState("output");

  return (
    <div style={{
      height: "100%",
      display: "flex",
      flexDirection: "column",
      background: "var(--bg-void)",
      borderTop: "1px solid var(--border-subtle)",
    }}>

      {/* Tabs */}
      <div style={{
        display: "flex",
        borderBottom: "1px solid var(--border-subtle)",
        padding: "0 8px",
        height: 30,
      }}>
        {TABS.map(({ id, label, icon: Icon }) => {

          const active = tab === id;

          return (
            <button
              key={id}
              onClick={() => setTab(id)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                padding: "0 10px",
                border: "none",
                borderBottom: `2px solid ${active ? "var(--accent)" : "transparent"}`,
                background: "transparent",
                color: active ? "var(--text-primary)" : "var(--text-faint)",
                fontSize: 11,
                cursor: "pointer",
              }}
            >
              <Icon size={11}/>
              {label}
            </button>
          );

        })}
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        overflow: "auto",
        padding: "10px 16px",
        fontFamily: "var(--font-code)",
        fontSize: 12,
      }}>

        {loading && (
          <div style={{ color: "var(--accent)" }}>
            Sending code to analyzer…
          </div>
        )}

        {!loading && result && tab === "output" && (

          <div style={{ lineHeight: 1.8 }}>

            <span style={{ color: "var(--green)" }}>
              <IconCheck size={12}/> Analysis complete
            </span>

            <br/>

            <span style={{ color: "var(--text-faint)" }}>Algorithm </span>
            <span style={{ color: "var(--text-primary)" }}>
              {result.algorithm_detected}
            </span>

            <br/>

            <span style={{ color: "var(--text-faint)" }}>Complexity </span>
            <span style={{ color: "var(--red)" }}>
              {result.time_complexity}
            </span>

            <span style={{ color: "var(--text-faint)" }}> → </span>

            <span style={{ color: "var(--teal)" }}>
              {result.improved_complexity}
            </span>

            <br/>

            <span style={{ color: "var(--text-faint)" }}>Suggestion </span>
            <span style={{ color: "var(--accent)" }}>
              {result.suggested_algorithm}
            </span>

            {/* Run Optimized Button */}

            {result.improved_code && (

              <div style={{ marginTop: 12 }}>

                <button
                  onClick={onRunOptimized}
                  style={{
                    padding: "6px 12px",
                    borderRadius: 6,
                    border: "1px solid var(--accent)",
                    background: "var(--accent)",
                    color: "#fff",
                    fontSize: 11,
                    cursor: "pointer"
                  }}
                >
                  Run Optimized Code
                </button>

              </div>

            )}

          </div>

        )}

        {!loading && result && tab === "problem" && (

          <div style={{ lineHeight: 1.8 }}>

            <div style={{ color: "var(--amber)" }}>
              ⚠ {result.problem}
            </div>

            <div style={{ color: "var(--text-muted)", fontSize: 11 }}>
              {result.explanation}
            </div>

          </div>

        )}

      </div>

    </div>
  );
}