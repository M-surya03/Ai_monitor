import { useEffect, useState } from "react";
import { progressApi } from "../services/progressApi";

import {
  StatCard,
  WeeklyChart,
  HistoryTable
} from "../components/progress/ProgressCards";

import { IconCPU, IconZap, IconClock, IconCode } from "../components/Icons";

export default function ProgressPage() {

  const [loading, setLoading] = useState(true);

  const [stats, setStats] = useState({
    totalSubmissions: 0,
    optimized: 0,
    avgRuntime: "-",
    algorithmsDetected: 0
  });

  const [weeklyData, setWeeklyData] = useState([]);
  const [history, setHistory] = useState([]);

  useEffect(() => {

    async function loadProgress() {

      try {

        const data = await progressApi.getProgress();

        setStats(data.stats);
        setWeeklyData(data.weekly);
        setHistory(data.submissions);

      } catch (err) {

        console.error("Progress load error:", err);

      } finally {

        setLoading(false);

      }
    }

    loadProgress();

  }, []);

  return (
    <div style={{ padding: "26px", display: "flex", flexDirection: "column", gap: 20 }}>

      <h2 style={{ fontSize: 20, fontWeight: 700 }}>
        Learning Progress
      </h2>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 14 }}>

        <StatCard icon={IconCode} label="Total Submissions" value={stats.totalSubmissions} loading={loading} />

        <StatCard icon={IconZap} label="Optimizations Found" value={stats.optimized} accent="var(--teal)" loading={loading} />

        <StatCard icon={IconClock} label="Average Runtime" value={stats.avgRuntime} loading={loading} />

        <StatCard icon={IconCPU} label="Algorithms Used" value={stats.algorithmsDetected} loading={loading} />

      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>

        <WeeklyChart data={weeklyData} loading={loading} />

      </div>

      <div>

        <h3 style={{ fontSize: 14, marginBottom: 10 }}>
          Recent Submissions
        </h3>

        <HistoryTable submissions={history} loading={loading} />

      </div>

    </div>
  );
}