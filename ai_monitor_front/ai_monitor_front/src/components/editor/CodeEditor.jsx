// components/editor/CodeEditor.jsx
// Lightweight syntax-highlighted editor — no Monaco dependency
// Uses a <textarea> overlaid on a <pre> for highlighting

import { useRef, useCallback } from "react";
import { highlight } from "../../utils/highlight";
import EditorToolbar from "./EditorToolbar";

export default function CodeEditor({
  lang,
  code,
  onCodeChange,
  onLangChange,
  onAnalyze,
  loading,
}) {
  const taRef = useRef(null);
  const lines = code.split("\n");

  const handleKeyDown = useCallback((e) => {
    // Tab → 2 spaces
    if (e.key === "Tab") {
      e.preventDefault();
      const s = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const next = code.slice(0, s) + "  " + code.slice(end);
      onCodeChange(next);
      requestAnimationFrame(() => {
        if (taRef.current) {
          taRef.current.selectionStart = taRef.current.selectionEnd = s + 2;
        }
      });
    }
    // ⌘↵ or Ctrl↵ → analyze
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      onAnalyze?.();
    }
    // Auto-close brackets/quotes
    const pairs = { "(": ")", "[": "]", "{": "}", '"': '"', "'": "'", "`": "`" };
    if (pairs[e.key] && e.key !== '"' && e.key !== "'" && e.key !== "`") {
      e.preventDefault();
      const s = e.target.selectionStart;
      const next = code.slice(0, s) + e.key + pairs[e.key] + code.slice(e.target.selectionEnd);
      onCodeChange(next);
      requestAnimationFrame(() => {
        if (taRef.current) {
          taRef.current.selectionStart = taRef.current.selectionEnd = s + 1;
        }
      });
    }
  }, [code, onCodeChange, onAnalyze]);

  const syncScroll = (e) => {
    const pre = e.target.previousSibling?.querySelector("pre");
    const nums = e.target.previousSibling?.querySelector(".line-nums");
    if (pre) pre.scrollTop = e.target.scrollTop;
    if (nums) nums.scrollTop = e.target.scrollTop;
  };

  return (
    <div style={{
      display: "flex", flexDirection: "column",
      height: "100%", width: "100%",
      background: "var(--bg-canvas)",
      overflow: "hidden",
    }}>
      <EditorToolbar
        lang={lang}
        onLangChange={onLangChange}
        onAnalyze={onAnalyze}
        loading={loading}
        lineCount={lines.length}
        charCount={code.length}
      />

      {/* Editor body */}
      <div style={{ flex: 1, overflow: "hidden", position: "relative", display: "flex" }}>

        {/* Line numbers */}
        <div
          className="line-nums"
          style={{
            width: 50, flexShrink: 0,
            padding: "14px 0 14px 0",
            overflow: "hidden",
            textAlign: "right",
            background: "var(--bg-canvas)",
            borderRight: "1px solid var(--border-subtle)",
            userSelect: "none",
          }}
        >
          {lines.map((_, i) => (
            <div key={i} style={{
              lineHeight: "21px",
              paddingRight: 12,
              fontFamily: "var(--font-code)", fontSize: 12,
              color: "var(--text-faint)",
            }}>
              {i + 1}
            </div>
          ))}
        </div>

        {/* Highlight + textarea */}
        <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
          {/* Highlight layer */}
          <pre style={{
            position: "absolute", inset: 0,
            margin: 0, padding: "14px 16px",
            overflow: "hidden",
            fontFamily: "var(--font-code)", fontSize: 13, lineHeight: "21px",
            color: "var(--text-primary)",
            whiteSpace: "pre",
            pointerEvents: "none",
            wordBreak: "normal",
            tabSize: 2,
          }}
            dangerouslySetInnerHTML={{ __html: highlight(code, lang) + "\n " }}
          />

          {/* Editable textarea */}
          <textarea
            ref={taRef}
            value={code}
            onChange={(e) => onCodeChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onScroll={syncScroll}
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            style={{
              position: "absolute", inset: 0,
              width: "100%", height: "100%",
              margin: 0, padding: "14px 16px",
              background: "transparent",
              border: "none", outline: "none",
              resize: "none",
              color: "transparent",
              caretColor: "var(--accent)",
              fontFamily: "var(--font-code)", fontSize: 13, lineHeight: "21px",
              whiteSpace: "pre",
              wordBreak: "normal",
              tabSize: 2,
              overflowX: "auto",
              overflowY: "auto",
              zIndex: 2,
            }}
          />
        </div>
      </div>

      {/* Status bar */}
      <div style={{
        height: "var(--statusbar-h)",
        display: "flex", alignItems: "center",
        padding: "0 14px",
        background: "var(--bg-void)",
        borderTop: "1px solid var(--border-subtle)",
        gap: 16,
        flexShrink: 0,
        fontFamily: "var(--font-code)", fontSize: 10,
        color: "var(--text-faint)",
        userSelect: "none",
      }}>
        <span style={{ color: "var(--accent)", fontWeight: 600 }}>
          {lang.charAt(0).toUpperCase() + lang.slice(1)}
        </span>
        <span>UTF-8</span>
        <span>LF</span>
        <span>Spaces: 2</span>
        <div style={{ flex: 1 }} />
        <span style={{ color: "var(--text-faint)" }}>
          Ln {lines.length}, Col {code.split("\n").pop()?.length ?? 0}
        </span>
      </div>
    </div>
  );
}