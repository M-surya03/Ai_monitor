import { createTheme } from "@mui/material/styles";

export const LANGS = ["javascript", "python", "java", "cpp"];

export const LANG_EXT = {
  javascript: "js",
  python: "py",
  java: "java",
  cpp: "cpp",
};

export const LANG_LABELS = {
  javascript: "JavaScript",
  python: "Python",
  java: "Java",
  cpp: "C++",
};

export const COMPLEXITY_COLOR = (val = "") => {
  if (!val) return "var(--text-muted)";
  if (val.includes("O(1)") || val.includes("O(log")) return "var(--teal)";
  if (/O\(n\)/.test(val)) return "var(--amber)";
  return "var(--red)";
};

export const COMPLEXITY_BG = (val = "") => {
  if (!val) return "transparent";
  if (val.includes("O(1)") || val.includes("O(log")) return "var(--teal-dim)";
  if (/O\(n\)/.test(val)) return "var(--amber-dim)";
  return "var(--red-dim)";
};

export const COMPLEXITY_BORDER = (val = "") => {
  if (!val) return "var(--border-subtle)";
  if (val.includes("O(1)") || val.includes("O(log")) return "var(--teal-border)";
  if (/O\(n\)/.test(val)) return "var(--amber-border)";
  return "var(--red-border)";
};

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#6366f1" },
    background: {
      default: "#020617",
      paper: "#0f172a"
    }
  },
  typography: {
    fontFamily: "JetBrains Mono, monospace"
  }
});

export default darkTheme;