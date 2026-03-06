package com.example.ai_monitor1.entity;

import jakarta.persistence.*;
import lombok.*;
@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserProgress {

    @Id
    private Long userId;

    private int totalSubmissions;

    private int currentStreak;

    private int longestStreak;
}