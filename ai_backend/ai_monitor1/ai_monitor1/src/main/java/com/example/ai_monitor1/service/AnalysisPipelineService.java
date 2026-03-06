package com.example.ai_monitor1.service;

import com.example.ai_monitor1.dto.*;
import com.example.ai_monitor1.entity.*;
import com.example.ai_monitor1.repository.*;
import com.example.ai_monitor1.util.PromptBuilder;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional
public class AnalysisPipelineService {

    private final StaticAnalysisService staticService;
    private final LLMService llmService;

    private final CodeSubmissionRepository submissionRepo;
    private final AnalysisResultRepository resultRepo;

    public AnalysisResultDTO analyze(CodeRequestDTO request) {

        log.info("========== ANALYSIS PIPELINE START ==========");

        /* ───────────── 1. Save Submission ───────────── */

        CodeSubmission submission = CodeSubmission.builder()
                .code(request.getCode())
                .language(request.getLanguage())
                .createdAt(LocalDateTime.now())
                .build();

        submissionRepo.save(submission);

        log.info("Saved submission id={}", submission.getSubmissionId());


        /* ───────────── 2. Static Analysis ───────────── */

        StaticAnalysisDTO staticResult;

        try {

            staticResult = staticService.analyze(request.getCode());

            log.info(
                    "Static analysis → algorithm={} complexity={}",
                    staticResult.getAlgorithmDetected(),
                    staticResult.getTimeComplexity()
            );

        } catch (Exception e) {

            log.error("Static analyzer failed: {}", e.getMessage());

            staticResult = new StaticAnalysisDTO(
                    "Unknown",
                    "Unknown",
                    List.of()
            );
        }


        /* ───────────── 3. Build Prompt ───────────── */

        String prompt = PromptBuilder.buildPrompt(
                request.getCode(),
                staticResult
        );


        /* ───────────── 4. LLM Analysis ───────────── */

        LLMResponseDTO llm;

        try {

            llm = llmService.generate(prompt);

            log.info(
                    "LLM result → algorithm={} complexity={}",
                    llm.getAlgorithm_detected(),
                    llm.getTime_complexity()
            );

        } catch (Exception e) {

            log.error("LLM call failed: {}", e.getMessage());
            throw new RuntimeException("LLM service unavailable");
        }

        if (llm == null) {
            throw new RuntimeException("LLM returned null response");
        }


        /* ───────────── 5. Optimization Check ───────────── */



        String currentComplexity = llm.getTime_complexity();
        String improvedComplexity = llm.getImproved_complexity();

        if (improvedComplexity == null || improvedComplexity.isBlank()) {

            llm.setSuggested_algorithm("Already Optimized");
            llm.setImproved_complexity(currentComplexity);
            llm.setImproved_code(request.getCode());

        }

        else if (currentComplexity.equalsIgnoreCase(improvedComplexity)) {

            llm.setSuggested_algorithm("Already Optimized");
            llm.setImproved_code(request.getCode());

        }

        /* ───────────── 6. Save Analysis Result ───────────── */

        AnalysisResult result = AnalysisResult.builder()
                .submission(submission)
                .algorithmDetected(llm.getAlgorithm_detected())
                .timeComplexity(llm.getTime_complexity())
                .problem(llm.getProblem())
                .explanation(llm.getExplanation())
                .suggestedAlgorithm(llm.getSuggested_algorithm())
                .improvedComplexity(llm.getImproved_complexity())
                .optimizedCode(llm.getImproved_code())
                .build();

        resultRepo.save(result);

        log.info("Saved result id={}", result.getResultId());


        /* ───────────── 7. Return DTO ───────────── */

        AnalysisResultDTO dto = new AnalysisResultDTO(
                result.getAlgorithmDetected(),
                result.getTimeComplexity(),
                result.getProblem(),
                result.getExplanation(),
                result.getSuggestedAlgorithm(),
                result.getImprovedComplexity(),
                result.getOptimizedCode()
        );

        log.info("========== ANALYSIS PIPELINE END ==========");

        return dto;
    }
}