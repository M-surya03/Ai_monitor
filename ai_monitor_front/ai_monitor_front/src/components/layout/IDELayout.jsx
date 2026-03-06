import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import TopNavbar from "./TopNavbar";
import ActivityBar from "./ActivityBar";
import CodeEditor from "../editor/CodeEditor";
import AIInsightsSidebar from "../analysis/AIInsightsSidebar";
import ResultPanel from "../analysis/ResultPanel";

const PLACEHOLDERS = {
  javascript: `function findDuplicate(arr) {
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) return arr[i];
    }
  }
  return -1;
}`,
  python: `def find_duplicate(arr):
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] == arr[j]:
                return arr[i]
    return -1`,
  java: `public int findDuplicate(int[] arr) {
    for (int i = 0; i < arr.length; i++)
        for (int j = i + 1; j < arr.length; j++)
            if (arr[i] == arr[j]) return arr[i];
    return -1;
}`,
  cpp: `int findDuplicate(vector<int>& arr) {
    for (int i = 0; i < arr.size(); i++)
        for (int j = i + 1; j < arr.size(); j++)
            if (arr[i] == arr[j]) return arr[i];
    return -1;
}`,
};

export default function IDELayout() {
  const navigate = useNavigate();

  const [lang, setLang] = useState("javascript");
  const [code, setCode] = useState(PLACEHOLDERS["javascript"]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeBar, setActiveBar] = useState("editor");
  const [bottomH, setBottomH] = useState(130);
  const [dragging, setDragging] = useState(false);

  const handleLangChange = useCallback((l) => {
    setLang(l);
    setCode(PLACEHOLDERS[l] || "");
    setResult(null);
  }, []);

  const handleAnalyzeOptimized = async () => {
    if (!result?.improved_code) return;

    try {
      setLoading(true);

      const res = await fetch("http://localhost:8080/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: lang,
          code: result.improved_code,
        }),
      });

      const data = await res.json();

      setResult({
        algorithm_detected: data.algorithmDetected,
        time_complexity: data.timeComplexity,
        problem: data.problem ?? "",
        explanation: data.explanation,
        suggested_algorithm: data.suggestedAlgorithm,
        improved_complexity: data.improvedComplexity ?? "",
        improved_code: data.improvedCode,
      });
    } catch (err) {
      console.error("Optimized analysis error:", err);
    } finally {
      setLoading(false);
    }
  };

  /* ---------------- Syntax Check ---------------- */

  const checkSyntax = async () => {
    try {
      const res = await fetch("http://localhost:5001/syntax-check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: lang,
          code: code,
        }),
      });

      const data = await res.json();

      if (!data.valid) {
        return data.error;
      }

      return null;
    } catch {
      return null;
    }
  };

  /* ---------------- Analyze Code ---------------- */

  const handleAnalyze = useCallback(async () => {
    if (!code.trim() || loading) return;

    setLoading(true);
    setResult(null);

    /* ---- Step 1: Syntax validation ---- */

    const syntaxError = await checkSyntax();

    if (syntaxError) {
      setResult({
        algorithm_detected: "Syntax Error",
        time_complexity: "-",
        problem: syntaxError,
        explanation: "Fix the syntax error before running analysis.",
        suggested_algorithm: "-",
        improved_complexity: "-",
        improved_code: "",
      });

      setLoading(false);
      return;
    }

    /* ---- Step 2: Call analyzer backend ---- */

    try {
      const res = await fetch("http://localhost:8080/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          language: lang,
          code: code,
        }),
      });

      if (!res.ok) throw new Error(`Server error ${res.status}`);

      const data = await res.json();

      setResult({
        algorithm_detected: data.algorithmDetected,
        time_complexity: data.timeComplexity,
        problem: data.problem ?? "",
        explanation: data.explanation,
        suggested_algorithm: data.suggestedAlgorithm,
        improved_complexity: data.improvedComplexity ?? "",
        improved_code: data.improvedCode,
      });
    } catch (err) {
      console.error("Analyze error:", err);

      await new Promise((r) => setTimeout(r, 1200));

      const mocks = {
        javascript: `function findDuplicate(arr) {
  const seen = new Set();
  for (const num of arr) {
    if (seen.has(num)) return num;
    seen.add(num);
  }
  return -1;
}`,
        python: `def find_duplicate(arr):
    seen = set()
    for num in arr:
        if num in seen:
            return num
        seen.add(num)
    return -1`,
        java: `public int findDuplicate(int[] arr) {
    Set<Integer> seen = new HashSet<>();
    for (int num : arr) {
        if (!seen.add(num)) return num;
    }
    return -1;
}`,
        cpp: `int findDuplicate(vector<int>& arr) {
    unordered_set<int> seen;
    for (int num : arr) {
        if (seen.count(num)) return num;
        seen.insert(num);
    }
    return -1;
}`,
      };

      setResult({
        algorithm_detected: "Bubble Sort Pattern",
        time_complexity: "O(n²)",
        problem: "Nested loops comparing elements repeatedly",
        explanation:
          "Each element is compared with every other element using nested loops, leading to quadratic growth in runtime.",
        suggested_algorithm: "Hash Set Lookup",
        improved_complexity: "O(n)",
        improved_code: mocks[lang],
      });
    } finally {
      setLoading(false);
    }
  }, [code, lang, loading]);

  /* ---------------- Bottom Resize ---------------- */

  const startDrag = useCallback(
    (e) => {
      e.preventDefault();
      setDragging(true);

      const startY = e.clientY;
      const startH = bottomH;

      const onMove = (ev) => {
        setBottomH(Math.max(80, Math.min(300, startH + (startY - ev.clientY))));
      };

      const onUp = () => {
        setDragging(false);
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
      };

      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    },
    [bottomH],
  );

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--bg-void)",
        overflow: "hidden",
      }}
    >
      <TopNavbar
        lang={lang}
        connected
        onProgressClick={() => navigate("/progress")}
      />

      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        <ActivityBar active={activeBar} onSelect={setActiveBar} />

        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
            <CodeEditor
              lang={lang}
              code={code}
              onCodeChange={setCode}
              onLangChange={handleLangChange}
              onAnalyze={handleAnalyze}
              loading={loading}
            />

            <AIInsightsSidebar
              result={result}
              loading={loading}
              lang={lang}
              originalCode={code}
            />
          </div>

          <div
            onMouseDown={startDrag}
            style={{
              height: 5,
              cursor: "ns-resize",
              flexShrink: 0,
              background: dragging ? "var(--accent)" : "var(--border-subtle)",
              transition: "background 0.15s",
            }}
          />

          <div
            style={{
              height: bottomH,
              flexShrink: 0,
              overflow: "hidden",
            }}
          >
            <ResultPanel
              result={result}
              loading={loading}
              onRunOptimized={handleAnalyzeOptimized}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
