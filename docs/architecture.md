# SentinelForge System Architecture

## 1. System Vision & Core Design Principle

**SentinelForge** is an enterprise-grade AI-powered data security, threat investigation, and DevSecOps platform designed to ingest security events, classify sensitive data, detect policy violations, correlate events into actionable incidents, assist analysts using a controlled AI security investigator, and recommend deterministic remediation actions.

### The Immutable Security Principle

> **"AI recommends. Deterministic controls enforce. Humans approve high-impact actions."**

The LLM is **never** treated as an administrative authority. All security-critical actions, credential rotations, account disables, and firewall rule updates must traverse deterministic authorization gates and require explicit human-in-the-loop (HITL) approval.

---

## 2. End-to-End High-Level Architecture

```mermaid
graph TD
    subgraph Client Layer
        WebClient["Web Console (React + Vite + Tailwind)"]
        SecOps["Security Analyst / Admin / Developer"]
        SecOps --> WebClient
    end

    subgraph Edge & Ingestion
        WebClient -->|HTTPS / WSS| APIGateway["FastAPI Gateway / Load Balancer"]
        ExtEvents["External Log Sources / CI/CD Scanners"] -->|REST POST /api/v1/events| APIGateway
    end

    subgraph Security Backend Core (FastAPI)
        APIGateway --> AuthMiddleware["Auth & RBAC Middleware (JWT / Bcrypt)"]
        AuthMiddleware --> RateLimiter["Progressive Rate Limiter"]
        RateLimiter --> NormLayer["Event Normalization Layer"]
        
        NormLayer --> RuleEngine["Deterministic Rule Engine"]
        NormLayer --> DLPEngine["DLP & Data Classification Engine"]
        
        RuleEngine --> CorrelationEngine["Security Correlation Engine"]
        DLPEngine --> CorrelationEngine
        
        CorrelationEngine --> IncidentService["Incident Management Service"]
    end

    subgraph Async & Storage Layer
        IncidentService -->|State Persistence| Postgres[(PostgreSQL 16 DB)]
        IncidentService -->|Job Queue / Cache| RedisQueue[(Redis Cache & Arq/Celery Queue)]
        AuthMiddleware -->|Audit Trail| AuditLog[(Immutable Audit Logs)]
    end

    subgraph AI Investigation Subsystem
        RedisQueue --> Worker["Async Background Worker"]
        Worker --> LangGraphAgent["LangGraph AI Security Investigator"]
        
        LangGraphAgent -->|Read-Only Tool| ToolEvents["search_security_events()"]
        LangGraphAgent -->|Read-Only Tool| ToolUser["get_user_activity()"]
        LangGraphAgent -->|Read-Only Tool| ToolPolicy["search_security_policies()"]
        LangGraphAgent -->|Read-Only Tool| ToolDLP["get_dlp_findings()"]
        LangGraphAgent -->|RAG Knowledge Retrieval| VectorKB["OWASP / Policy Vector RAG"]
        
        LangGraphAgent --> StructValidator["Pydantic Structured Output Validator"]
        StructValidator --> RemediationSuggester["Remediation Action Recommender"]
    end

    subgraph Human-In-The-Loop (HITL) Enforcement
        RemediationSuggester --> PendingAction["remediation_actions (Status: PENDING_APPROVAL)"]
        PendingAction -.->|Notification| WebClient
        WebClient -->|Admin Review & Explicit Sign-off| ApprovalGate{"Human Approver (Admin)"}
        ApprovalGate -->|Approved| ExecSimulator["Simulated / Guarded Remediation Execution"]
        ApprovalGate -->|Rejected| AuditReject["Logged Rejection in Audit Trail"]
    end
```

---

## 3. Core Component Subsystems

### 3.1 Authentication & RBAC Engine
- **Password Security**: Argon2id / Bcrypt password hashing with high work factor. Plaintext passwords never hit logs or databases.
- **Session & Tokens**: Short-lived JWT access tokens (15–30 min) with cryptographically secure refresh token rotation and revocation list in Redis.
- **RBAC Matrix**: Enforced at FastAPI dependency level (`require_permission` / `require_role`).
  - **Admin**: Full administrative, policy, user management, and remediation approval authority.
  - **Security Analyst**: Incident investigation, log inspection, AI agent triggering, report generation, remediation recommendation.
  - **Developer**: Scans submission, own finding reviews, DLP inspection on personal artifacts.
  - **Viewer**: Read-only dashboard telemetry.

### 3.2 Event Ingestion & Normalization
- Heterogeneous event ingestion (`syslog`, cloud audit logs, web server logs, auth events, file operations).
- Ingestion schema validation with Pydantic.
- Normalization mapping:
  - Principal identity (`user`, `username`, `principal`) $\rightarrow$ `user_id / actor`
  - Network indicators (`client_ip`, `remote_addr`) $\rightarrow$ `source_ip`
  - Standardized severity (`INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### 3.3 Deterministic Rule Engine
Evaluates real-time event sequences without probabilistic hallucination:
1. **Brute Force Detection**: $\ge N$ failed authentication events within sliding window $T$.
2. **Privilege Escalation**: Attempt by standard user to invoke admin/sensitive APIs.
3. **Suspicious Data Access**: Rapid, broad-scope access across `RESTRICTED` or `CONFIDENTIAL` assets.
4. **Secret Exposure**: Unmasked secret or token patterns identified in code or logs.
5. **Impossible / Anomalous Access**: Geo-velocity or atypical access hours/locations.

### 3.4 Data Classification & DLP Engine
- **Regex & Pattern Classifiers**: API keys (AWS, GitHub, Slack, OpenAI, Stripe), JWT tokens, private keys, connection strings, emails, phone numbers.
- **Entropy Analysis**: Shannon entropy calculation for high-randomness string detection (e.g., base64 private keys).
- **Classification Hierarchy**:
  - `PUBLIC`: General non-sensitive data.
  - `INTERNAL`: Operational internal data.
  - `CONFIDENTIAL`: Business-sensitive data / PII.
  - `RESTRICTED`: High-risk credentials, master keys, production financial data.
- **DLP Actions**: `ALLOW`, `WARN`, `BLOCK`, `QUARANTINE_REVIEW`.
- **Secret Masking Guarantee**: Secrets are masked immediately (`AKIA****************MPLE`) before database storage or UI display.

### 3.5 Security Correlation Engine & Incident Pipeline
- Correlates isolated security events sharing common entities (`actor`, `source_ip`, `target_asset`, time window).
- Computes **Explainable Risk Score (0–100)**:
  $$\text{Risk Score} = \min(100, \sum \text{Factor Weights})$$
  Example breakdown:
  - $+25$ Restricted data involved
  - $+20$ Privileged account target
  - $+20$ Repeated failed authentication
  - $+15$ Unusual access pattern
  - $+11$ Correlated high-severity events
- Assembles timeline and dynamic attack graph relationships.

### 3.6 LangGraph AI Security Investigator
- Orchestrated state-machine agent:
  1. `START`
  2. `LoadIncident`
  3. `CollectEvidence`
  4. `AnalyzeEvents`
  5. `CheckUserActivity`
  6. `CheckPermissions`
  7. `RetrieveSecurityPolicy` (Authorized RAG)
  8. `CorrelateAttackChain`
  9. `GenerateFindings`
  10. `GenerateRecommendations`
  11. `HumanReviewGate`
  12. `END`
- **Agent Guardrails**:
  - Read-only tools only. No direct write/execution tools.
  - Strict system prompt separation to mitigate prompt injection.
  - Enforced Pydantic output schema validation with fallback mechanisms.
  - Distinguishes **FACT**, **INFERENCE**, and **RECOMMENDATION**.

### 3.7 Threat Modeling Engine (STRIDE)
- Analyzes software components, data flows, boundaries, and entry points.
- Categorizes threats into **STRIDE**:
  - **S**poofing
  - **T**ampering
  - **R**epudiation
  - **I**nformation Disclosure
  - **D**enial of Service
  - **E**levation of Privilege
- Tracks lifecycle: `OPEN`, `MITIGATED`, `ACCEPTED`, `FALSE_POSITIVE`.

---

## 4. Layered Backend Architecture

```
FastAPI Router (API Layer)
       │ (Request DTO / Validation)
       ▼
Service Layer (Business Logic & Deterministic Gates)
       │
       ├──► Rules / DLP / Correlation / AI Engines
       ▼
Repository Layer (Data Access & Query Optimization)
       │ (Parameterized Queries / Async SQLAlchemy)
       ▼
PostgreSQL Database / Redis
```

---

## 5. Observability, Logging, & Auditing
- **Structured JSON Logging**: Every log entry includes `timestamp`, `request_id`, `actor_id`, `module`, and `level`.
- **Immutable Audit Trail**: Security actions (`LOGIN`, `ROLE_CHANGE`, `POLICY_UPDATE`, `REMEDIATION_APPROVAL`) written to append-only audit log table.
- **Health & Readiness Probes**: `/health` and `/ready` endpoints verifying database and Redis connectivity.
