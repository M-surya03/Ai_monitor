package com.example.ai_monitor1.dto;


import lombok.*;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class StaticAnalysisDTO {

    private String algorithmDetected;
    private String timeComplexity;
    private List<String> issues;
}