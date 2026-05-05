package com.acsel.demo.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PolicyController {

    private static final Map<String, Map<String, Object>> POLICIES = new HashMap<>();

    static {
        POLICIES.put("POL-1001", policy("POL-1001", "active", true, "auto", "retail", 15000000.0, "ARS"));
        POLICIES.put("POL-1002", policy("POL-1002", "active", true, "auto", "retail", 18000000.0, "ARS"));
        POLICIES.put("POL-1003", policy("POL-1003", "suspended", false, "robo", "retail", 12000000.0, "ARS"));
        POLICIES.put("POL-1004", policy("POL-1004", "active", true, "hogar", "premium", 25000000.0, "ARS"));
        POLICIES.put("POL-1005", policy("POL-1005", "active", true, "incendio", "commercial", 50000000.0, "ARS"));
    }

    @GetMapping("/api/policies/{policyNumber}")
    public Map<String, Object> getPolicy(@PathVariable String policyNumber) {
        return POLICIES.getOrDefault(policyNumber, policy(policyNumber, "not_found", false, null, null, null, null));
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok", "service", "mock-java-service");
    }

    private static Map<String, Object> policy(
        String policyNumber,
        String status,
        Boolean coverageActive,
        String productLine,
        String customerSegment,
        Double sumInsured,
        String currency
    ) {
        Map<String, Object> result = new HashMap<>();
        result.put("policy_number", policyNumber);
        result.put("status", status);
        result.put("coverage_active", coverageActive);
        result.put("product_line", productLine);
        result.put("customer_segment", customerSegment);
        result.put("sum_insured", sumInsured);
        result.put("currency", currency);
        return result;
    }
}
