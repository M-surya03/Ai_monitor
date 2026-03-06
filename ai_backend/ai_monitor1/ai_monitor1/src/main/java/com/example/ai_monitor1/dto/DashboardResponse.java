package com.example.ai_monitor1.dto;

import lombok.*;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class DashboardResponse {

    private Stats stats;
    private List<WeeklyData> weekly;
    private List<SubmissionHistory> submissions;

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class Stats {

        private int totalSubmissions;
        private int optimized;
        private String avgRuntime;
        private int algorithmsDetected;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class WeeklyData {

        private String day;
        private int count;
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class SubmissionHistory {

        private String algorithmDetected;
        private String language;
        private String timeComplexity;
        private String improvedComplexity;
        private String createdAt;
    }
}