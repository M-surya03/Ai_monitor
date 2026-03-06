package com.example.ai_monitor1.repository;

import com.example.ai_monitor1.entity.CodeSubmission;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CodeSubmissionRepository extends JpaRepository<CodeSubmission, Long> {

    // Explicitly fetch ALL submissions ordered by date descending.
    // Using findAll() via JPA to avoid any implicit query limits.
    @Query("""
        SELECT cs
        FROM CodeSubmission cs
        LEFT JOIN FETCH cs.analysisResult
        ORDER BY cs.createdAt DESC
        """)
    List<CodeSubmission> findAllOrderedByDate();

}