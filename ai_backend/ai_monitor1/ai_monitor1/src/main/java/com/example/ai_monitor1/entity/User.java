package com.example.ai_monitor1.entity;

import jakarta.persistence.*;
import lombok.*;
@Entity
@Data
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String email;
    private String password;
}