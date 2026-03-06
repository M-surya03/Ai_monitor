package com.example.ai_monitor1.controller;

import com.example.ai_monitor1.dto.AnalysisResultDTO;
import com.example.ai_monitor1.dto.CodeRequestDTO;
import com.example.ai_monitor1.service.AnalysisPipelineService;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class CodeAnalysisController {

    private final AnalysisPipelineService pipeline;

    @PostMapping("/analyze")
    public ResponseEntity<AnalysisResultDTO> analyze(@RequestBody CodeRequestDTO request) {
        if (request.getCode() == null || request.getCode().isBlank()) {
            throw new RuntimeException("Code cannot be empty");
        }
        return ResponseEntity.ok(pipeline.analyze(request));
    }
}