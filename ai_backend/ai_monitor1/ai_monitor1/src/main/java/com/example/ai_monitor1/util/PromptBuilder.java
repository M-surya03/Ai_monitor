package com.example.ai_monitor1.util;

import com.example.ai_monitor1.dto.StaticAnalysisDTO;

public class PromptBuilder {

    public static String buildPrompt(String code, StaticAnalysisDTO analysis) {

        return """
You are an expert software engineer.

Analyze the following code and detect the algorithm.

Code:
%s

Static analysis hint:
Algorithm detected: %s

IMPORTANT:
Verify the algorithm and complexity yourself.

Return ONLY JSON:

{
 "algorithm_detected": "",
 "time_complexity": "",
 "problem": "",
 "explanation": "",
 "suggested_algorithm": "",
 "improved_complexity": "",
 "improved_code": ""
}

Rules:
- If the algorithm is already optimal, set suggested_algorithm to "Already Optimized".
- If improvement exists, provide a better algorithm.
- improved_code must be a full optimized Python implementation.
""".formatted(code, analysis.getAlgorithmDetected());
    }
}