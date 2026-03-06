package com.example.ai_monitor1.service;

import com.example.ai_monitor1.dto.DashboardResponse;
import com.example.ai_monitor1.entity.CodeSubmission;
import com.example.ai_monitor1.repository.AnalysisResultRepository;
import com.example.ai_monitor1.repository.CodeSubmissionRepository;

import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;

import java.time.DayOfWeek;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DashboardService {

    private final AnalysisResultRepository resultRepo;
    private final CodeSubmissionRepository submissionRepo;

    public DashboardResponse getDashboard() {

        /* ───────────── Stats ───────────── */

        int totalSubmissions = resultRepo.countSubmissions();
        int optimized        = resultRepo.countOptimized();
        int algorithms       = resultRepo.countAlgorithms();

        DashboardResponse.Stats stats = new DashboardResponse.Stats(
                totalSubmissions,
                optimized,
                "-",
                algorithms
        );

        /* ───────────── Weekly Activity ───────────── */

        // Reuse the same full list — avoids a second DB call
        List<CodeSubmission> all = submissionRepo.findAllOrderedByDate(); // ← fixed method name

        Map<DayOfWeek, Integer> weeklyMap = new EnumMap<>(DayOfWeek.class);
        for (DayOfWeek d : DayOfWeek.values()) weeklyMap.put(d, 0);

        for (CodeSubmission s : all) {
            if (s.getCreatedAt() != null) {
                DayOfWeek day = s.getCreatedAt().getDayOfWeek();
                weeklyMap.put(day, weeklyMap.get(day) + 1);
            }
        }

        List<DashboardResponse.WeeklyData> weekly = weeklyMap.entrySet()
                .stream()
                .sorted(Map.Entry.comparingByKey())
                .map(e -> new DashboardResponse.WeeklyData(
                        e.getKey().name().substring(0, 3),
                        e.getValue()
                ))
                .toList();

        /* ───────────── Recent Submission History ───────────── */

        // Uses the same eagerly-fetched list — no N+1, no hidden limit
        List<DashboardResponse.SubmissionHistory> history = all.stream()
                .filter(s -> s.getAnalysisResult() != null)
                .map(s -> new DashboardResponse.SubmissionHistory(
                        s.getAnalysisResult().getAlgorithmDetected(),
                        s.getLanguage(),
                        s.getAnalysisResult().getTimeComplexity(),
                        s.getAnalysisResult().getImprovedComplexity(),
                        s.getCreatedAt().toString()
                ))
                .collect(Collectors.toList());

        /* ───────────── Build Response ───────────── */

        return DashboardResponse.builder()
                .stats(stats)
                .weekly(weekly)
                .submissions(history)
                .build();
    }
}