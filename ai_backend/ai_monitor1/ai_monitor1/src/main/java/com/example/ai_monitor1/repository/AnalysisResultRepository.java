package com.example.ai_monitor1.repository;



import com.example.ai_monitor1.entity.AnalysisResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface AnalysisResultRepository extends JpaRepository<AnalysisResult, Long> {

    @Query("SELECT COUNT(ar) FROM AnalysisResult ar")
    int countSubmissions();

    @Query("SELECT COUNT(ar) FROM AnalysisResult ar WHERE ar.improvedComplexity IS NOT NULL")
    int countOptimized();

    @Query("SELECT COUNT(DISTINCT ar.algorithmDetected) FROM AnalysisResult ar")
    int countAlgorithms();

}