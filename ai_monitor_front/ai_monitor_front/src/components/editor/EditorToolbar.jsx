import LanguageSelector from "./LanguageSelector";
import AnalyzeButton from "../analysis/AnalyzeButton";

export default function EditorToolbar({
  lang,
  onLangChange,
  onAnalyze,
  loading,
  lineCount = 0,
  charCount = 0,
}) {
  return (
    <div style={{
      height: "var(--tab-h)",
      display: "flex",
      alignItems: "center",
      gap: 8,
      padding: "0 10px 0 12px",
      borderBottom: "1px solid var(--border-subtle)",
      background: "var(--bg-canvas)",
      flexShrink: 0,
    }}>
      {/* File tab */}
      <div style={{
        display: "flex", alignItems: "center", gap: 6,
        padding: "4px 10px",
        background: "var(--bg-surface)",
        border: "1px solid var(--border-subtle)",
        borderBottom: "1px solid var(--bg-surface)",
        borderRadius: "5px 5px 0 0",
        marginBottom: -1,
      }}>
        <span style={{
          width: 7, height: 7, borderRadius: "50%",
          background: "var(--accent)", opacity: 0.8,
        }} />
        <span style={{
          fontFamily: "var(--font-code)", fontSize: 11,
          color: "var(--text-secondary)",
        }}>
          main.{lang === "javascript" ? "js" : lang === "python" ? "py" : lang === "java" ? "java" : "cpp"}
        </span>
        {/* Unsaved dot */}
        <span style={{
          width: 5, height: 5, borderRadius: "50%",
          background: "var(--amber)", opacity: 0.7,
        }} />
      </div>

      <div style={{ flex: 1 }} />

      {/* Stats */}
      <div style={{
        fontFamily: "var(--font-code)", fontSize: 10,
        color: "var(--text-faint)",
        display: "flex", gap: 10,
      }}>
        <span>{lineCount} lines</span>
        <span style={{ color: "var(--border-default)" }}>·</span>
        <span>{charCount} chars</span>
      </div>

      {/* Language selector */}
      <LanguageSelector value={lang} onChange={onLangChange} />

      {/* Analyze */}
      <AnalyzeButton onClick={onAnalyze} loading={loading} />
    </div>
  );
}