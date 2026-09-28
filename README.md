# SentinelForge 🛡️

### Enterprise AI-Powered Data Security, Threat Investigation & DevSecOps Platform

[![Security Gate: Enforced](https://img.shields.io/badge/Security_Controls-Deterministic_Enforcement-blue.svg)](#)
[![AI Architecture](https://img.shields.io/badge/AI_Agent-LangGraph_State_Machine-purple.svg)](#)
[![RBAC Policy](https://img.shields.io/badge/RBAC-Server--Side_Gated-green.svg)](#)
[![HITL](https://img.shields.io/badge/High--Risk_Actions-Human--in--the--Loop-orange.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

---

## 1. Executive Summary

**SentinelForge** is a modern cybersecurity engineering platform engineered to ingest high-volume security telemetry, inspect sensitive data streams, classify findings according to data sensitivity, correlate disparate events into coherent incidents, and assist SecOps analysts through a controlled AI security investigator.

### The Foundational Security Tenet

```
   ┌───────────────────────┐
   │     AI RECOMMENDS     │  (LangGraph Agent synthesizes evidence & suggests actions)
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │ DETERMINISTIC ENFORCES│  (Bcrypt, RBAC, Pydantic validation, Masking, DLP rules)
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │    HUMANS APPROVE     │  (Zero autonomous destructive actions; Admin approval required)
   └───────────────────────┘
```

The AI agent is never treated as an unrestricted security authority. All remediation actions (e.g., account lockouts, API key revocations) require deterministic authorization checks and explicit **human-in-the-loop (HITL)** approval.

---

## 2. Platform Architecture

```mermaid
graph TD
    Client["Enterprise Security Console (React + Vite + Tailwind)"] -->|HTTPS / WSS| Gateway["FastAPI Edge Gateway"]
    Sources["Cloud Audit / Syslog / AppSec Scanners"] -->|POST /api/v1/events| Gateway

    subgraph Security Backend (FastAPI Core)
        Gateway --> Auth["Bcrypt + JWT Authentication & RBAC Middleware"]
        Auth --> RateLimit["Token-Bucket Rate Limiter"]
        RateLimit --> Normalizer["Event Normalization Engine"]
        Normalizer --> RuleEngine["Deterministic Rule Engine"]
        Normalizer --> DLPEngine["DLP & Secret Masking Engine"]
        
        RuleEngine --> CorrelationEngine["Correlation & Risk Scoring Engine (0-100)"]
        DLPEngine --> CorrelationEngine
        CorrelationEngine --> IncidentDB[(PostgreSQL 16 Database)]
    end

    subgraph AI Investigation Subsystem
        IncidentDB --> Worker["Async Job Worker (Redis Queue)"]
        Worker --> LangGraphAgent["LangGraph AI Security Investigator"]
        LangGraphAgent --> ReadTools["Controlled Read-Only Tools"]
        LangGraphAgent --> RAGKB["Authorized Vector Policy Knowledge Base"]
        LangGraphAgent --> OutputValidator["Pydantic Structured Output Validation"]
    end

    subgraph Governance & Human Approval
        OutputValidator --> PendingRemediation["Remediation Action (PENDING_APPROVAL)"]
        PendingRemediation --> AdminGate{"Admin Approval Gate"}
        AdminGate -->|Approve| SimulatedExec["Simulated Remediation Execution"]
        AdminGate -->|Reject| AuditTrail[(Immutable Audit Log)]
    end
```

---

## 3. Key Capabilities & Technical Features

- **Robust Authentication & Deterministic RBAC**: Argon2id/Bcrypt password hashing, short-lived JWT access tokens with rotation, progressive rate limiting, and server-side RBAC enforcement (`Admin`, `Analyst`, `Developer`, `Viewer`).
- **Validated Event Ingestion & Normalization**: Universal ingestion API accepting diverse formats and mapping them into canonical entity schemas.
- **Explainable Risk Scoring (0–100)**: Transparent risk scoring showing exact additive factors (e.g., $+25$ Restricted data, $+20$ Privileged account, $+20$ Repeated failed login).
- **Data Classification & DLP Engine**: Deterministic pattern matching and Shannon entropy analysis detecting secrets (AWS, GitHub, Slack, DB strings, JWTs) and PII. Immediate automated masking (`AKIA****************MPLE`) ensures zero plaintext secrets in storage.
- **STRIDE Threat Modeling**: Architecture threat modeling component categorizing threats into Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege.
- **LangGraph AI Security Investigator**: Multi-step state machine orchestrator equipped exclusively with read-only inspection tools. Fortified against prompt injection with strict context separation.
- **Human-in-the-Loop Remediation**: AI recommends actions; execution is strictly blocked until an authorized Administrator reviews the risk and grants approval.
- **Immutable Security Audit Logs**: Append-only auditing for all security-sensitive operations.
- **DevSecOps & Cloud Ready**: Multi-stage Docker containerization, GitHub Actions security scanning (SAST, secret auditing, dependency checks), and production-grade Terraform AWS IaC modules.

---

## 4. Technology Stack

| Layer | Technologies | Justification |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Lucide Icons, Recharts | High performance, type safety, dense enterprise security aesthetics |
| **Backend** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (asyncio) | High-throughput asynchronous API, strict schema validation, type safety |
| **Database** | PostgreSQL 16 (asyncpg), Alembic | ACID compliance, relational integrity, JSONB indexing for payloads |
| **Cache & Queue** | Redis 7 | High-speed rate-limiting, session revocation, async background job queue |
| **AI Orchestration** | LangGraph, OpenAI GPT-4o-mini, Embeddings | State machine agent execution, structured JSON outputs, deterministic fallbacks |
| **DevSecOps & IaC** | Docker, GitHub Actions, Terraform (AWS) | Reproducible environments, automated security gates, cloud infrastructure |

---

## 5. Development Seed Accounts

> **Notice:** Demo environment with synthetic security data only. Never use production credentials.

| Role | Email | Password | Scope of Authority |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@sentinelforge.local` | `SentinelAdmin123!` | Full control: Users, Policies, Remediation Approval |
| **Analyst** | `analyst@sentinelforge.local` | `SentinelAnalyst123!` | Incident investigation, AI trigger, Evidence inspection |
| **Developer**| `developer@sentinelforge.local` | `SentinelDev123!` | Artifact scanning, personal finding review |
| **Viewer** | `viewer@sentinelforge.local` | `SentinelViewer123!` | Read-only dashboard telemetry |

---

## 6. Monorepo Directory Layout

```
sentinelforge/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (/v1)
│   │   ├── core/            # Configuration, security, database session
│   │   ├── models/          # SQLAlchemy relational models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic & deterministic control gates
│   │   ├── repositories/    # Database query layer
│   │   ├── rules/           # Deterministic rule engine
│   │   ├── dlp/             # Data classification & secret detection
│   │   ├── correlation/     # Incident correlation & risk scoring
│   │   ├── threat_modeling/ # STRIDE threat modeling engine
│   │   ├── ai/              # LangGraph agent, tools, prompts, RAG
│   │   └── audit/           # Immutable audit logging
│   └── tests/               # Unit, integration, and security tests
├── frontend/                # React + TypeScript + Tailwind console
├── docs/                    # Architecture, Database, Threat Model, ADRs
├── infra/                   # Terraform AWS infrastructure modules
├── .github/workflows/       # DevSecOps CI/CD pipelines
├── docker-compose.yml       # Local multi-service orchestration
└── README.md
```

---

## 7. Documentation Index

- [System Architecture](file:///e:/React%20Projects/SentinelForge/docs/architecture.md)
- [Database Design & Schema](file:///e:/React%20Projects/SentinelForge/docs/database.md)
- [STRIDE Threat Model](file:///e:/React%20Projects/SentinelForge/docs/threat-model.md)
- [Implementation Roadmap](file:///e:/React%20Projects/SentinelForge/docs/roadmap.md)
