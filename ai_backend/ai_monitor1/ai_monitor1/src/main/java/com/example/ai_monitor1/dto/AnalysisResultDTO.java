package com.example.ai_monitor1.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AnalysisResultDTO {

    private String algorithmDetected;

    private String timeComplexity;

    private String problem;

    private String explanation;

    private String suggestedAlgorithm;

    private String improvedComplexity;

    private String improvedCode;
}