package com.example.ai_monitor1.service;

import com.example.ai_monitor1.dto.StaticAnalysisDTO;

import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.*;

@Service
@RequiredArgsConstructor
public class StaticAnalysisService {

    private final WebClient webClient;

    public StaticAnalysisDTO analyze(String code) {

        Map<String, String> request = new HashMap<>();
        request.put("code", code);

        Map response =
                webClient.post()
                        .uri("http://localhost:5000/analyze")
                        .bodyValue(request)
                        .retrieve()
                        .bodyToMono(Map.class)
                        .block();

        String algorithm = (String) response.get("algorithm_detected");
        String complexity = (String) response.get("time_complexity");

        List<String> issues = (List<String>) response.get("issues");

        return new StaticAnalysisDTO(
                algorithm,
                complexity,
                issues
        );
    }
}