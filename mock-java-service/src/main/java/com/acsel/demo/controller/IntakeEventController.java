package com.acsel.demo.controller;

import java.util.Map;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class IntakeEventController {

    @PostMapping("/api/claims/intake-events")
    public Map<String, Object> receiveIntakeEvent(@RequestBody Map<String, Object> payload) {
        return Map.of(
            "status", "received",
            "source", "mock-java-service",
            "claim_id", payload.get("claim_id")
        );
    }
}
