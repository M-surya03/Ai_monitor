// components/analysis/AIInsightsSidebar.jsx
// Replaces old AIInsightsSidebar — full analysis panel with tabs

import { useState } from "react";
import { IconCPU, IconDiff, IconCopy, IconAlert, IconCheck } from "../Icons";
import AlgorithmCard from "./AlgorithmCard";
import ComplexityCard from "./ComplexityCard";
import CodeDiffViewer from "../diff/CodeDiffViewer";

import { highlight } from "../../utils/highlight";
import { StaggerList } from "../animations";

const TABS = ["Analysis", "Diff"];

// Skeleton shimmer block
function Skel({ w = "100%", h = 14, mb = 0 }) {
  return (
    <div style={{
      width: w, height: h, marginBottom: mb, borderRadius: 4,
      background: "linear-gradient(90deg, var(--bg-surface) 25%, var(--bg-elevated) 50%, var(--bg-surface) 75%)",
      backgroundSize: "400px 100%",
      animation: "shimmer 1.4s infinite",
    }} />
  );
}

// Inline code view
function InlineCode({ code, lang, label, accent = "var(--teal)" }) {
  const [copied, setCopied] = useState(false);
  const lines = (code || "").split("\n");

  return (
    <div style={{
      background: "var(--bg-void)",
      border: "1px solid var(--border-subtle)",
      borderRadius: 7,
      overflow: "hidden",
    }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "6px 12px",
        borderBottom: "1px solid var(--border-subtle)",
      }}>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: accent }}>
          {label}
        </span>
        <button
          onClick={() => {
            navigator.clipboard.writeText(code || "");
            setCopied(true);
            setTimeout(() => setCopied(false), 1800);
          }}
          style={{
            display: "flex", alignItems: "center", gap: 4,
            background: "none", border: "none", cursor: "pointer",
            color: copied ? "var(--teal)" : "var(--text-faint)",
            fontFamily: "var(--font-ui)", fontSize: 10,
            transition: "color 0.15s",
          }}
        >
          <IconCopy size={10} />
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <div style={{ overflow: "auto", maxHeight: 220 }}>
        {lines.map((ln, i) => (
          <div key={i} style={{ display: "flex", minHeight: 20 }}>
            <span style={{
              width: 32, textAlign: "right", paddingRight: 10, flexShrink: 0,
              fontFamily: "var(--font-code)", fontSize: 10, lineHeight: "20px",
              color: "var(--text-faint)", userSelect: "none",
            }}>
              {i + 1}
            </span>
            <span
              style={{
                fontFamily: "var(--font-code)", fontSize: 11, lineHeight: "20px",
                color: "var(--text-primary)", whiteSpace: "pre", paddingRight: 12,
              }}
              dangerouslySetInnerHTML={{ __html: highlight(ln, lang) }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function AIInsightsSidebar({ result, loading, lang, originalCode }) {
  const [tab, setTab] = useState("Analysis");

  return (
    <aside style={{
      width: "var(--sidebar-w)",
      flexShrink: 0,
      borderLeft: "1px solid var(--border-subtle)",
      background: "var(--bg-canvas)",
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        display: "flex", alignItems: "center",
        padding: "0 4px",
        borderBottom: "1px solid var(--border-subtle)",
        flexShrink: 0, height: "var(--tab-h)",
      }}>
        {TABS.map((t) => {
          const active = tab === t;
          const disabled = !result && t === "Diff";
          return (
            <button
              key={t}
              onClick={() => !disabled && setTab(t)}
              disabled={disabled}
              style={{
                padding: "0 14px", height: "100%",
                border: "none",
                borderBottom: `2px solid ${active ? "var(--accent)" : "transparent"}`,
                background: "transparent",
                color: disabled
                  ? "var(--text-faint)"
                  : active
                  ? "var(--text-primary)"
                  : "var(--text-muted)",
                fontFamily: "var(--font-ui)", fontSize: 11, fontWeight: active ? 600 : 400,
                cursor: disabled ? "not-allowed" : "pointer",
                opacity: disabled ? 0.4 : 1,
                transition: "color 0.15s",
              }}
            >
              {t}
            </button>
          );
        })}

        <div style={{ flex: 1 }} />
        <div style={{
          display: "flex", alignItems: "center", gap: 5,
          marginRight: 10,
          fontSize: 9, fontWeight: 700, letterSpacing: "0.08em", textTransform: "uppercase",
          color: "var(--accent)",
        }}>
          <IconCPU size={11} />
          AI Insights
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, overflow: "auto", padding: 14 }}>

        {/* Empty state */}
        {!loading && !result && (
          <div style={{
            height: "100%", display: "flex", flexDirection: "column",
            alignItems: "center", justifyContent: "center",
            gap: 12, padding: "0 24px", textAlign: "center",
          }}>
            <div style={{
              width: 44, height: 44, borderRadius: 12,
              background: "var(--accent-dim)", border: "1px solid var(--accent-border)",
              display: "flex", alignItems: "center", justifyContent: "center",
              color: "var(--accent)",
            }}>
              <IconCPU size={18} />
            </div>
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 5 }}>
                No analysis yet
              </div>
              <div style={{ fontSize: 11, color: "var(--text-faint)", lineHeight: 1.7 }}>
                Write or paste code in the editor, then press{" "}
                <strong style={{ color: "var(--accent)" }}>Run Analysis</strong>
              </div>
            </div>
          </div>
        )}

        {/* Skeleton */}
        {loading && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 6 }}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2.5"
                style={{ animation: "spin 0.75s linear infinite" }}>
                <circle cx="12" cy="12" r="10" strokeOpacity="0.15" />
                <path d="M12 2a10 10 0 0 1 10 10" />
              </svg>
              <span style={{ fontSize: 11, color: "var(--accent)", fontWeight: 500 }}>Running analysis…</span>
            </div>
            <Skel w="65%" h={14} mb={4} />
            <Skel w="90%" h={52} mb={4} />
            <Skel w="75%" h={14} mb={4} />
            <Skel w="100%" h={40} mb={4} />
            <Skel w="55%" h={14} mb={4} />
            <Skel w="100%" h={90} />
          </div>
        )}

        {/* Analysis tab */}
        {!loading && result && tab === "Analysis" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12, animation: "fade-up 0.3s ease" }}>

            <AlgorithmCard
              detected={result.algorithm_detected}
              suggested={result.suggested_algorithm}
            />

            <ComplexityCard
              before={result.time_complexity}
              after={result.improved_complexity}
            />

            {/* Problem */}
            <div style={{
              background: "var(--red-dim)", border: "1px solid var(--red-border)",
              borderRadius: 8, padding: 12,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 7, color: "var(--red)" }}>
                <IconAlert size={11} />
                <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                  Problem
                </span>
              </div>
              <p style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.7, margin: 0 }}>
                {result.problem}
              </p>
            </div>

            {/* Explanation */}
            <div style={{
              background: "var(--teal-dim)", border: "1px solid var(--teal-border)",
              borderRadius: 8, padding: 12,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 7, color: "var(--teal)" }}>
                <IconCheck size={11} />
                <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase" }}>
                  Explanation
                </span>
              </div>
              <p style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.7, margin: 0 }}>
                {result.explanation}
              </p>
            </div>

            {/* Optimized code */}
            <div>
              <div style={{
                fontSize: 9, fontWeight: 700, letterSpacing: "0.1em",
                textTransform: "uppercase", color: "var(--text-muted)",
                marginBottom: 8,
              }}>
                Optimized Code
              </div>
              <InlineCode
                code={result.improved_code}
                lang={lang}
                label={result.suggested_algorithm}
                accent="var(--teal)"
              />
            </div>

            {/* View diff CTA */}
            <button
              onClick={() => setTab("Diff")}
              style={{
                display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                padding: "8px 14px",
                background: "var(--bg-surface)",
                border: "1px solid var(--border-default)",
                borderRadius: 6,
                color: "var(--text-secondary)",
                fontFamily: "var(--font-ui)", fontSize: 11, fontWeight: 500,
                cursor: "pointer",
                transition: "all 0.15s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "var(--accent-border)";
                e.currentTarget.style.color = "var(--accent)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "var(--border-default)";
                e.currentTarget.style.color = "var(--text-secondary)";
              }}
            >
              <IconDiff size={12} />
              View Side-by-Side Diff
            </button>
          </div>
        )}

        {/* Diff tab */}
        {!loading && result && tab === "Diff" && (
          <div style={{ animation: "fade-up 0.3s ease" }}>
            <div style={{
              fontSize: 9, fontWeight: 700, letterSpacing: "0.1em",
              textTransform: "uppercase", color: "var(--text-muted)",
              marginBottom: 10,
            }}>
              Side-by-Side Diff
            </div>
            <CodeDiffViewer
              original={originalCode}
              optimized={result.improved_code}
              lang={lang}
            />
          </div>
        )}
      </div>
    </aside>
  );
}