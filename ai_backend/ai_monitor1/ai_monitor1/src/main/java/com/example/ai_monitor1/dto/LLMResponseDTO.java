package com.example.ai_monitor1.dto;


import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class LLMResponseDTO {

    private String algorithm_detected;
    private String time_complexity;
    private String problem;
    private String explanation;
    private String suggested_algorithm;
    private String improved_complexity;
    private String improved_code;
}