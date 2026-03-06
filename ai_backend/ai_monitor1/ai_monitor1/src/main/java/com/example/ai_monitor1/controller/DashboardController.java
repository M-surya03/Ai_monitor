package com.example.ai_monitor1.controller;

import com.example.ai_monitor1.dto.DashboardResponse;
import com.example.ai_monitor1.entity.UserProgress;
import com.example.ai_monitor1.service.DashboardService;
import com.example.ai_monitor1.service.UserProgressService;

import lombok.RequiredArgsConstructor;

import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping
    public DashboardResponse getDashboard() {
        return dashboardService.getDashboard();
    }
}