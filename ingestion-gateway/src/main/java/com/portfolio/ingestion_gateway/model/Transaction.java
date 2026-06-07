package com.portfolio.ingestion_gateway.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "transactions") // Tells PostgreSQL to name the table 'transactions'
public class Transaction {

    @Id
    private String id; // Primary Key
    
    private String merchantId;
    private double amount;
    private String status; // e.g., PENDING, APPROVED, BLOCKED

    // New AI Fields
    private int riskScore;
    private String aiExplanation;

    // Default constructor required by JPA
    public Transaction() {}

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getMerchantId() { return merchantId; }
    public void setMerchantId(String merchantId) { this.merchantId = merchantId; }

    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public int getRiskScore() { return riskScore; }
    public void setRiskScore(int riskScore) { this.riskScore = riskScore; }

    public String getAiExplanation() { return aiExplanation; }
    public void setAiExplanation(String aiExplanation) { this.aiExplanation = aiExplanation; }
}