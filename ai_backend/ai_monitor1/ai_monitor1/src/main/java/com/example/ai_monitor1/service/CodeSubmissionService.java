package com.example.ai_monitor1.service;

import com.example.ai_monitor1.entity.CodeSubmission;
import com.example.ai_monitor1.entity.User;
import com.example.ai_monitor1.repository.CodeSubmissionRepository;

import lombok.RequiredArgsConstructor;

import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class CodeSubmissionService {


    private final CodeSubmissionRepository submissionRepository;

    public CodeSubmission saveSubmission(User user, String code, String language) {

        CodeSubmission submission = CodeSubmission.builder()
                .user(user)
                .code(code)
                .language(language)
                .createdAt(LocalDateTime.now())
                .build();

        return submissionRepository.save(submission);
    }

}
