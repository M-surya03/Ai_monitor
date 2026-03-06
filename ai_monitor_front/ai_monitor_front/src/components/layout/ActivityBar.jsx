import { useState } from "react";
import {
  IconCode,
  IconAnalytics,
  IconSearch,
  IconGit,
  IconTerminal,
  IconSettings,
} from "../Icons";

const ITEMS = [
  { id: "editor", icon: IconCode, title: "Explorer" },
  { id: "search", icon: IconSearch, title: "Search" },
  { id: "git", icon: IconGit, title: "Source Control" },
  { id: "analysis", icon: IconAnalytics, title: "Analysis" },
  { id: "terminal", icon: IconTerminal, title: "Terminal" },
];

export default function ActivityBar({ active = "editor", onSelect }) {

  const [hovered, setHovered] = useState(null);

  return (
    <aside
      style={{
        width: "var(--activity-w)",
        background: "var(--bg-canvas)",
        borderRight: "1px solid var(--border-subtle)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "8px 0",
        gap: 2,
        flexShrink: 0,
        userSelect: "none",
      }}
    >

      {ITEMS.map(({ id, icon: Icon, title }) => {

        const isActive = active === id;
        const isHovered = hovered === id;

        return (
          <button
            key={id}
            title={title}
            onClick={() => onSelect?.(id)}
            onMouseEnter={() => setHovered(id)}
            onMouseLeave={() => setHovered(null)}
            style={{
              width: 36,
              height: 36,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              background: isActive
                ? "var(--accent-dim)"
                : isHovered
                ? "var(--bg-overlay)"
                : "transparent",
              color: isActive
                ? "var(--accent)"
                : isHovered
                ? "var(--text-secondary)"
                : "var(--text-faint)",
              transition: "all 0.15s",
              position: "relative",
            }}
          >

            {isActive && (
              <span
                style={{
                  position: "absolute",
                  left: -8,
                  top: "50%",
                  transform: "translateY(-50%)",
                  width: 2,
                  height: 16,
                  background: "var(--accent)",
                  borderRadius: "0 2px 2px 0",
                }}
              />
            )}

            <Icon size={16} />

          </button>
        );
      })}

      <div style={{ flex: 1 }} />

      <button
        title="Settings"
        onMouseEnter={() => setHovered("settings")}
        onMouseLeave={() => setHovered(null)}
        style={{
          width: 36,
          height: 36,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          border: "none",
          borderRadius: 8,
          cursor: "pointer",
          background: hovered === "settings" ? "var(--bg-overlay)" : "transparent",
          color: hovered === "settings" ? "var(--text-secondary)" : "var(--text-faint)",
          transition: "all 0.15s",
        }}
      >
        <IconSettings size={16} />
      </button>

    </aside>
  );
}