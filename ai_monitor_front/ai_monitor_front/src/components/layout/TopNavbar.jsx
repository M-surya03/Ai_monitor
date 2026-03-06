import { useNavigate } from "react-router-dom";
import { IconBolt, IconAnalytics, IconCode } from "../Icons";
import { LANG_EXT } from "../../theme";

export default function TopNavbar({ lang = "javascript", connected = true, onProgressClick }) {

  const ext = LANG_EXT[lang] ?? "js";
  const navigate = useNavigate();

  return (
    <header
      style={{
        height: "var(--topbar-h)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 14px",
        background: "var(--bg-canvas)",
        borderBottom: "1px solid var(--border-subtle)",
        flexShrink: 0,
        userSelect: "none",
        position: "relative",
        zIndex: 20,
      }}
    >

      {/* Left section */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>

        {/* Traffic lights */}
        <div style={{ display: "flex", gap: 6 }}>
          {["#f85149", "#f0883e", "#3fb950"].map((c, i) => (
            <div
              key={i}
              style={{
                width: 11,
                height: 11,
                borderRadius: "50%",
                background: c,
                opacity: 0.85,
                boxShadow: `0 0 5px ${c}55`,
              }}
            />
          ))}
        </div>

        {/* Breadcrumb */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 4,
            fontFamily: "var(--font-code)",
            fontSize: 11,
            color: "var(--text-muted)",
            marginLeft: 4,
          }}
        >
          <span style={{ color: "var(--text-faint)" }}>code-analyzer</span>
          <span style={{ color: "var(--border-default)" }}>/</span>
          <span style={{ color: "var(--text-secondary)" }}>src</span>
          <span style={{ color: "var(--border-default)" }}>/</span>
          <span style={{ color: "var(--text-primary)" }}>main.{ext}</span>
        </div>

      </div>

      {/* Center section */}
      <div style={{ display: "flex", alignItems: "center", gap: 2 }}>

        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 7, marginRight: 10 }}>
          <div
            style={{
              width: 22,
              height: 22,
              borderRadius: 6,
              background: "var(--accent-dim)",
              border: "1px solid var(--accent-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--accent)",
            }}
          >
            <IconBolt size={12} />
          </div>

          <span
            style={{
              fontSize: 12,
              fontWeight: 600,
              color: "var(--text-muted)",
              letterSpacing: "0.02em",
            }}
          >
            AI Code Analyzer
          </span>
        </div>

        {/* Navigation */}
        {[
          { label: "Editor", icon: IconCode, action: () => navigate("/analyzer"), active: true },
          { label: "Progress", icon: IconAnalytics, action: onProgressClick, active: false },
        ].map(({ label, icon: Icon, action, active }) => (
          <button
            key={label}
            onClick={action}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 5,
              padding: "4px 10px",
              border: "none",
              background: active ? "var(--accent-dim)" : "transparent",
              borderRadius: 5,
              color: active ? "var(--accent)" : "var(--text-faint)",
              fontFamily: "var(--font-ui)",
              fontSize: 11,
              fontWeight: active ? 600 : 400,
              cursor: "pointer",
              transition: "all 0.15s",
            }}
          >
            <Icon size={11} />
            {label}
          </button>
        ))}

      </div>

      {/* Right section */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>

        {/* LLM Badge */}
        <div
          style={{
            padding: "3px 8px",
            background: "var(--bg-surface)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 4,
            fontFamily: "var(--font-code)",
            fontSize: 10,
            color: "var(--text-muted)",
          }}
        >
          <span style={{ color: "var(--accent)", fontWeight: 600 }}>LLM</span> · Ollama
        </div>

        {/* Connection status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 5,
            padding: "3px 8px",
            background: connected ? "var(--green-dim)" : "var(--red-dim)",
            border: `1px solid ${connected ? "var(--green-border)" : "var(--red-border)"}`,
            borderRadius: 4,
          }}
        >
          <div
            style={{
              width: 5,
              height: 5,
              borderRadius: "50%",
              background: connected ? "var(--green)" : "var(--red)",
            }}
          />

          <span
            style={{
              fontSize: 10,
              fontWeight: 600,
              color: connected ? "var(--green)" : "var(--red)",
              fontFamily: "var(--font-code)",
            }}
          >
            {connected ? "Connected" : "Offline"}
          </span>
        </div>

      </div>
    </header>
  );
}