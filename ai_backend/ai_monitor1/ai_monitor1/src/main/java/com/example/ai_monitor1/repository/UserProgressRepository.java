package com.example.ai_monitor1.repository;



import com.example.ai_monitor1.entity.UserProgress;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserProgressRepository extends JpaRepository<UserProgress, Long> {
}