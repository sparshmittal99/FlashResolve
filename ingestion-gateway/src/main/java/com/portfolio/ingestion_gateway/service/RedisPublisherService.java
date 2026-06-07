package com.portfolio.ingestion_gateway.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.portfolio.ingestion_gateway.model.Transaction;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class RedisPublisherService {

    @Autowired
    private StringRedisTemplate redisTemplate; // Spring handles this one perfectly

    // FIX: We just build the ObjectMapper ourselves!
    private final ObjectMapper objectMapper = new ObjectMapper(); 

    public void publishToQueue(Transaction transaction) {
        try {
            // Convert Java object to JSON
            String transactionJson = objectMapper.writeValueAsString(transaction);

            // Push to Redis
            redisTemplate.opsForList().leftPush("anomaly_queue", transactionJson);

            System.out.println("✅ Successfully pushed Transaction " + transaction.getId() + " to Redis anomaly_queue.");

        } catch (Exception e) {
            System.err.println("❌ Failed to push to Redis: " + e.getMessage());
        }
    }
}