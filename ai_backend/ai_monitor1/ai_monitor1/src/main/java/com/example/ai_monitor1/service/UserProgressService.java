package com.example.ai_monitor1.service;

import com.example.ai_monitor1.entity.UserProgress;
import com.example.ai_monitor1.repository.UserProgressRepository;

import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserProgressService {

    private final UserProgressRepository progressRepository;

    // ── Update progress after every submission ─────────────────
    public void updateProgress(Long userId) {

        UserProgress progress = progressRepository.findById(userId)
                .orElse(UserProgress.builder()
                        .userId(userId)
                        .totalSubmissions(0)
                        .currentStreak(0)
                        .longestStreak(0)
                        .build());

        progress.setTotalSubmissions(progress.getTotalSubmissions() + 1);
        progress.setCurrentStreak(progress.getCurrentStreak() + 1);

        if (progress.getCurrentStreak() > progress.getLongestStreak()) {
            progress.setLongestStreak(progress.getCurrentStreak());
        }

        progressRepository.save(progress);
    }

    // ── Fetch progress stats ─────────────────
    public UserProgress getUserProgress(Long userId) {

        return progressRepository.findById(userId)
                .orElse(UserProgress.builder()
                        .userId(userId)
                        .totalSubmissions(0)
                        .currentStreak(0)
                        .longestStreak(0)
                        .build());
    }
}