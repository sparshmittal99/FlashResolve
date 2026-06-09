package com.portfolio.ingestion_gateway.controller;

import com.portfolio.ingestion_gateway.model.Transaction;
import com.portfolio.ingestion_gateway.repository.TransactionRepository;
import com.portfolio.ingestion_gateway.service.RedisPublisherService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@RestController
@RequestMapping("/api/transactions")
// 🟢 Whitelists your exact live Angular frontend URL and your local development server
@CrossOrigin(origins = {"https://flashresolvedashboard.onrender.com", "http://localhost:4200"})
public class TransactionController {

    @Autowired
    private RedisPublisherService redisPublisherService;

    @Autowired
    private TransactionRepository transactionRepository;

    // 1. Receives data from Angular Dashboard, sets to PROCESSING, and pushes to Redis
    @PostMapping
    public ResponseEntity<Transaction> ingestTransaction(@RequestBody Transaction transaction) {
        if (transaction.getId() == null || transaction.getId().isEmpty()) {
            transaction.setId(UUID.randomUUID().toString());
        }

        // 🚀 Force safe default UI states regardless of what the payload sent
        transaction.setStatus("PROCESSING");
        transaction.setRiskScore(0);
        transaction.setAiExplanation("Awaiting AI evaluation...");

        // Save initial state to PostgreSQL
        transactionRepository.save(transaction);
        System.out.println("💾 Saved to DB [PROCESSING]: $" + transaction.getAmount() + " from " + transaction.getMerchantId());

        // Push to Upstash Redis for the Python Worker
        redisPublisherService.publishToQueue(transaction);

        // Return the exact JSON object back to Angular
        return ResponseEntity.ok(transaction);
    }

    // 2. The Webhook for the Python AI Worker to submit its final decision
    @PutMapping("/{id}/result")
    public ResponseEntity<String> updateTransactionResult(@PathVariable String id, @RequestBody Transaction aiResult) {
        Optional<Transaction> existingTxOpt = transactionRepository.findById(id);

        if (existingTxOpt.isPresent()) {
            Transaction tx = existingTxOpt.get();
            tx.setRiskScore(aiResult.getRiskScore());
            tx.setAiExplanation(aiResult.getAiExplanation());
            tx.setStatus(aiResult.getStatus()); 

            transactionRepository.save(tx);
            System.out.println("✅ DB Updated! Transaction " + id + " marked as: " + tx.getStatus());
            return ResponseEntity.ok("Result saved successfully.");
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    // 3. Fetches all transactions for the live Angular Dashboard
    @GetMapping
    public ResponseEntity<List<Transaction>> getAllTransactions() {
        List<Transaction> transactions = transactionRepository.findAll();
        return ResponseEntity.ok(transactions);
    }
}