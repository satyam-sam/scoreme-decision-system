# Architecture Document
## ScoreMe Decision System

---

## 1. System Overview
A configurable workflow decision platform that processes
loan/onboarding requests through rule evaluation,
external service calls, and state management.

---

## 2. Components

| Component | File | Responsibility |
|---|---|---|
| REST API | app.py | Request intake, routing |
| Rule Engine | engines/rule_engine.py | Rule evaluation |
| Workflow Engine | engines/workflow_engine.py | Decision logic |
| External Service | services/external_service.py | Credit bureau simulation |
| Retry Service | services/retry_service.py | Fault tolerance |
| Audit Logger | services/audit_logger.py | Full audit trail |
| Database | database/db.py | MySQL persistence |

---

## 3. Data Flow
```
Client Request
     ↓
FastAPI (app.py)
     ↓
Idempotency Check (MySQL)
     ↓
External Credit Bureau (with 3x retry)
     ↓
Rule Engine (rules.json)
     ↓
Workflow Engine
     ↓
MySQL Save + Audit Log
     ↓
Response to Client
```

---

## 4. Key Design Decisions

### Configurable Rules
Rules in JSON — change without code rewrite.

### Idempotency
MySQL-backed — survives server restarts.

### Retry with Exponential Backoff
3 retries: 1s → 2s → 4s wait.

### External Dependency Simulation
20% failure rate simulates real-world API issues.

---

## 5. Trade-offs

| Decision | Benefit | Trade-off |
|---|---|---|
| MySQL over Redis | ACID, persistent | Slower than in-memory |
| JSON config | Easy to change | No UI editor |
| Sync processing | Simple | Not async/queue based |
| FastAPI | Fast, auto-docs | Python only |

---

## 6. Scaling Considerations


- **Horizontal**: Multiple EC2 instances + Load Balancer
- **Database**: MySQL → AWS RDS with read replicas
- **Queue**: Add Celery + Redis for async processing
- **Cache**: Redis for frequent rule lookups
- **Config**: Move rules to database with version history