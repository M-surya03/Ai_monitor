package com.example.ai_monitor1.service;

import com.example.ai_monitor1.dto.LLMResponseDTO;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class LLMService {

    private final WebClient webClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final String API_URL = "http://localhost:5001/llm/analyze";

    public LLMResponseDTO generate(String prompt) {

        try {

            String rawJson = webClient.post()
                    .uri(API_URL)
                    .bodyValue(Map.of("prompt", prompt))
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            log.info("LLM raw response: {}", rawJson);

            if (rawJson == null || rawJson.isBlank()) {
                throw new RuntimeException("LLM returned empty response");
            }
            String cleaned = rawJson.trim();

            if (cleaned.startsWith("```")) {
                cleaned = cleaned
                        .replaceAll("(?s)^```[a-zA-Z]*\\n?", "")
                        .replaceAll("```\\s*$", "")
                        .trim();
            }

            Map<String, Object> map;

            try {
                map = objectMapper.readValue(cleaned, Map.class);
            }
            catch (Exception ex) {

                log.warn("JSON parsing failed, attempting recovery");

                cleaned = cleaned
                        .replace("\n", "\\n")
                        .replace("\r", "");

                map = objectMapper.readValue(cleaned, Map.class);
            }
            log.info("Parsed keys from LLM: {}", map.keySet());

            return new LLMResponseDTO(
                    get(map,"algorithm_detected"),
                    get(map,"time_complexity"),
                    get(map,"problem"),
                    get(map,"explanation"),
                    get(map,"suggested_algorithm"),
                    get(map,"improved_complexity"),
                    get(map,"improved_code")
            );

        } catch (Exception e) {

            log.error("LLM processing failed: {}", e.getMessage());

            throw new RuntimeException("LLM service error: " + e.getMessage());
        }
    }

    private String get(Map<String,Object> map,String key){
        Object v = map.get(key);
        return v == null ? "" : v.toString();
    }
}