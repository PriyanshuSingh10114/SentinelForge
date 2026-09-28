# Architecture Decision Records (ADRs)

## Index of Decisions
- [ADR-001: PostgreSQL with Asyncpg for Canonical Store](#adr-001-postgresql-with-asyncpg-for-canonical-store)
- [ADR-002: FastAPI Async Architecture](#adr-002-fastapi-async-architecture)
- [ADR-003: LangGraph for Deterministic AI Security Agent Orchestration](#adr-003-langgraph-for-deterministic-ai-security-agent-orchestration)
- [ADR-004: Redis for Distributed State, Token Blacklisting & Rate Limiting](#adr-004-redis-for-distributed-state-token-blacklisting--rate-limiting)
- [ADR-005: Strict Server-Side RBAC Dependencies](#adr-005-strict-server-side-rbac-dependencies)
- [ADR-006: Human-in-the-Loop (HITL) Approval Gates for Remediations](#adr-006-human-in-the-loop-hitl-approval-gates-for-remediations)
- [ADR-007: Phased Cloud Infrastructure & Least-Privilege IAM](#adr-007-phased-cloud-infrastructure--least-privilege-iam)

---

### ADR-001: PostgreSQL with Asyncpg for Canonical Store
- **Context**: SentinelForge requires ACID guarantees for relational security data, incident timelines, user accounts, and immutable audit logs.
- **Decision**: Adopt PostgreSQL 16 managed with SQLAlchemy 2.0 and `asyncpg` driver.
- **Alternatives**: MongoDB (rejected due to weak relational integrity on audit and permission cascades); DynamoDB (rejected due to complex multi-entity querying).
- **Consequences**: High reliability, foreign key constraints prevent orphan incidents, robust JSONB support for normalized event payloads.

### ADR-002: FastAPI Async Architecture
- **Context**: The platform handles concurrent high-throughput security event ingestion alongside long-running AI investigations.
- **Decision**: Use FastAPI with Python 3.12 and asynchronous request pipelines.
- **Alternatives**: Flask/Django (blocking by default or heavier footprint).
- **Consequences**: Native OpenAPI documentation, Pydantic v2 strict type validation, async non-blocking I/O.

### ADR-003: LangGraph for Deterministic AI Security Agent Orchestration
- **Context**: Unconstrained autonomous LLM agents present unpredictable execution paths and prompt injection risks.
- **Decision**: Structure AI investigations using LangGraph state machine with read-only inspection tools and deterministic offline fallback.
- **Alternatives**: AutoGPT / CrewAI (too autonomous and prone to looping or unauthorized command execution).
- **Consequences**: Reproducible step-by-step investigation graphs (`LOAD_INCIDENT` -> `COLLECT_EVIDENCE` -> `ANALYZE` -> `SYNTHESIZE`), explicit structured schema outputs, zero autonomous destructive actions.

### ADR-004: Redis for Distributed State, Token Blacklisting & Rate Limiting
- **Context**: Fast authentication checks, JWT revocation blacklist lookups, and progressive lockout counters must not bottleneck the primary SQL database.
- **Decision**: Deploy Redis 7 for caching and rate limiting.
- **Alternatives**: In-memory Python dictionaries (incompatible with horizontal scaling); Memcached (lacks pub/sub and key expiration events).
- **Consequences**: Sub-millisecond blacklist lookups and distributed lock capability.

### ADR-005: Strict Server-Side RBAC Dependencies
- **Context**: Frontend authorization can be bypassed by constructing direct HTTP requests.
- **Decision**: Implement centralized FastAPI dependencies (`require_role`, `require_permission`) checking the database role and permission tables on every protected endpoint.
- **Alternatives**: Client-side UI toggles only (vulnerable to OWASP A01 Broken Access Control).
- **Consequences**: Defense-in-depth enforcement: unauthorized requests immediately return 403 Forbidden with zero data disclosure.

### ADR-006: Human-in-the-Loop (HITL) Approval Gates for Remediations
- **Context**: Autonomous AI remediation can lead to catastrophic business downtime or denial of service if tricked by adversarial inputs.
- **Decision**: Enforce the invariant: *"AI recommends. Deterministic controls enforce. Humans approve high-impact actions."* All remediation actions enter `PENDING_APPROVAL` status and can only be triggered by an Admin.
- **Alternatives**: Autonomous remediation agents (unacceptable operational and security risk).
- **Consequences**: Complete accountability, mandatory audit trail with administrator identity attached to every execution.

### ADR-007: Phased Cloud Infrastructure & Least-Privilege IAM
- **Context**: Deploying untested infrastructure directly to AWS risks cost overruns and misconfigured security groups.
- **Decision**: Staged delivery pipeline: Local -> Docker Compose -> Security Testing -> CI/CD -> AWS Terraform with zero wildcard admin permissions.
- **Alternatives**: Ad-hoc AWS Console click-ops (unversioned, prone to security drift).
- **Consequences**: Modular Infrastructure as Code, reproducible staging environments, verifiable IAM boundaries.
