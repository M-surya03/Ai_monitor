import { useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  IconBolt,
  IconArrowRight,
  IconCPU,
  IconZap,
  IconCode,
  IconAnalytics
} from "../components/Icons";

const FEATURES = [
  {
    icon: IconCPU,
    label: "Algorithm Detection",
    desc: "Identifies sorting, search, and graph patterns",
  },
  {
    icon: IconZap,
    label: "Complexity Analysis",
    desc: "Pinpoints Big-O bottlenecks in your code",
  },
  {
    icon: IconBolt,
    label: "AI Optimization",
    desc: "Generates optimized algorithm alternatives",
  },
  {
    icon: IconAnalytics,
    label: "Code Insights",
    desc: "Understand how your algorithm behaves",
  },
];

export default function HomePage() {

  const navigate = useNavigate();

  const [hoverMain, setHoverMain] = useState(false);
  const [hoverSecondary, setHoverSecondary] = useState(false);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg-void)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "0 24px",
        position: "relative",
        overflow: "hidden",
      }}
    >

      {/* Grid Background */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          backgroundImage: `
            linear-gradient(var(--border-subtle) 1px, transparent 1px),
            linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px)
          `,
          backgroundSize: "48px 48px",
          opacity: 0.32,
        }}
      />

      {/* Glow Effect */}
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          background: "radial-gradient(circle, #7c6dfa16 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          position: "relative",
          zIndex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 36,
          maxWidth: 580,
          textAlign: "center",
          animation: "fade-up 0.6s cubic-bezier(.22,.68,0,1.1) both",
        }}
      >

        {/* Logo */}
        <div
          style={{
            width: 60,
            height: 60,
            borderRadius: 16,
            background: "var(--accent-dim)",
            border: "1px solid var(--accent-border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--accent)",
            boxShadow: "0 0 40px #7c6dfa2a",
          }}
        >
          <IconBolt size={26} />
        </div>

        {/* Headline */}
        <div>
          <h1
            style={{
              fontFamily: "var(--font-ui)",
              fontSize: "clamp(30px, 5vw, 46px)",
              fontWeight: 700,
              lineHeight: 1.12,
              color: "var(--text-primary)",
              letterSpacing: "-0.03em",
              margin: 0,
            }}
          >
            AI Code{" "}
            <span
              style={{
                background: "linear-gradient(135deg, var(--accent) 30%, var(--teal))",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              Analyzer
            </span>
          </h1>

          <p
            style={{
              marginTop: 14,
              fontSize: 15,
              color: "var(--text-muted)",
              lineHeight: 1.7,
            }}
          >
            Paste your code and instantly receive algorithm detection,
            complexity analysis, and optimized implementations.
          </p>
        </div>

        {/* Buttons */}
        <div style={{ display: "flex", gap: 10 }}>

          <button
            onClick={() => navigate("/analyzer")}
            onMouseEnter={() => setHoverMain(true)}
            onMouseLeave={() => setHoverMain(false)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "12px 28px",
              background: hoverMain
                ? "var(--accent-hover)"
                : "var(--accent)",
              border: "none",
              borderRadius: 8,
              color: "#fff",
              fontFamily: "var(--font-ui)",
              fontSize: 14,
              fontWeight: 600,
              cursor: "pointer",
              transition: "all 0.2s",
              boxShadow: hoverMain ? "var(--accent-glow)" : "none",
            }}
          >
            <IconCode size={14} />
            Open Editor
            <IconArrowRight size={13} />
          </button>

          <button
            onClick={() => navigate("/progress")}
            onMouseEnter={() => setHoverSecondary(true)}
            onMouseLeave={() => setHoverSecondary(false)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 7,
              padding: "12px 22px",
              background: hoverSecondary
                ? "var(--bg-overlay)"
                : "var(--bg-surface)",
              border: "1px solid var(--border-subtle)",
              borderRadius: 8,
              color: "var(--text-secondary)",
              fontFamily: "var(--font-ui)",
              fontSize: 14,
              fontWeight: 500,
              cursor: "pointer",
              transition: "all 0.2s",
            }}
          >
            <IconAnalytics size={13} />
            View Insights
          </button>

        </div>

        {/* Features */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 10,
            width: "100%",
          }}
        >
          {FEATURES.map(({ icon: Icon, label, desc }, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: 10,
                padding: "14px 16px",
                background: "var(--bg-canvas)",
                border: "1px solid var(--border-subtle)",
                borderRadius: 10,
                textAlign: "left",
              }}
            >
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 7,
                  flexShrink: 0,
                  background: "var(--accent-dim)",
                  border: "1px solid var(--accent-border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--accent)",
                }}
              >
                <Icon size={13} />
              </div>

              <div>
                <div
                  style={{
                    fontSize: 12,
                    fontWeight: 600,
                    color: "var(--text-primary)",
                    marginBottom: 2,
                  }}
                >
                  {label}
                </div>

                <div
                  style={{
                    fontSize: 11,
                    color: "var(--text-faint)",
                    lineHeight: 1.5,
                  }}
                >
                  {desc}
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}