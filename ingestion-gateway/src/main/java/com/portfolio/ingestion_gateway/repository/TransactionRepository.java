package com.portfolio.ingestion_gateway.repository;

import com.portfolio.ingestion_gateway.model.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, String> {
    // Spring Boot automatically implements save(), findById(), etc. for us!
}