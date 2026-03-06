package com.example.ai_monitor1.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table(name = "analysis_results")
public class AnalysisResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long resultId;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "submission_id", nullable = false)
    private CodeSubmission submission;

    private String algorithmDetected;
    private String timeComplexity;

    @Column(columnDefinition = "TEXT")
    private String problem;

    @Column(columnDefinition = "TEXT")
    private String explanation;

    private String suggestedAlgorithm;
    private String improvedComplexity;

    @Column(columnDefinition = "TEXT")
    private String optimizedCode;
}