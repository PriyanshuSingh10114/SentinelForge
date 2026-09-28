<div align="center">

# SentinelForge

### **Enterprise AI-Powered Data Security, Threat Investigation & DevSecOps Platform**

*A portfolio-grade cybersecurity engineering platform pairing deterministic security controls with an AI-assisted threat investigator.*

<br/>

<p align="center">
  <!-- Core Tech Badges -->
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI"/></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React_18-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"/></a>
  <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"/></a>
  <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS"/></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL_16-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/></a>
  <a href="https://redis.io/"><img src="https://img.shields.io/badge/Redis_7-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis"/></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/></a>
  <a href="https://www.terraform.io/"><img src="https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white" alt="Terraform"/></a>
  <a href="https://aws.amazon.com/"><img src="https://img.shields.io/badge/AWS_Cloud-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white" alt="AWS"/></a>
</p>

<p align="center">
  <!-- Security Posture Badges -->
  <img src="https://img.shields.io/badge/Security_Controls-Deterministic_Enforced-00C853?style=flat-square&logo=shield" alt="Security Controls"/>
  <img src="https://img.shields.io/badge/AI_Agent-LangGraph_State_Machine-7C4DFF?style=flat-square&logo=openai" alt="LangGraph AI"/>
  <img src="https://img.shields.io/badge/RBAC-Server--Side_Gated-0288D1?style=flat-square&logo=auth0" alt="RBAC Gated"/>
  <img src="https://img.shields.io/badge/High--Risk_Actions-Human--in--the--Loop-FF6D00?style=flat-square&logo=probot" alt="HITL Approvals"/>
  <img src="https://img.shields.io/badge/OWASP_Top_10-Tested_&_Verified-2E7D32?style=flat-square&logo=checkmarx" alt="OWASP Verified"/>
  <img src="https://img.shields.io/badge/Tests-33%20Passed-brightgreen?style=flat-square&logo=pytest" alt="Pytest Passing"/>
  <img src="https://img.shields.io/badge/License-MIT-F57F17?style=flat-square" alt="MIT License"/>
</p>

---

### **Engineering Tenet**
> **"AI recommends. Deterministic controls enforce. Humans approve high-impact actions."**

</div>

<br/>

## 👨‍💻 Author Details & Organization

<table align="center" width="100%">
  <tr>
    <td align="center" width="30%">
      <img src="https://github.com/PriyanshuSingh10114.png" width="130px;" alt="Priyanshu Singh" style="border-radius: 50%; box-shadow: 0 4px 12px rgba(0,0,0,0.3);"/><br/>
      <b>Priyanshu Singh</b><br/>
      <sub>Senior Security & Full-Stack Cloud Engineer</sub>
    </td>
    <td width="70%">
      <p><b>Bio:</b> Cybersecurity software engineer specializing in AI/LLM orchestration, application security, cloud-native architectures, and DevSecOps pipelines.</p>
      <p>
        <a href="https://github.com/PriyanshuSingh10114"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>
        <a href="mailto:priyanshusingh22340@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/></a>
        <a href="https://linkedin.com"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
      </p>
      <p>
        <b>Affiliations & Companies:</b><br/>
        <img src="https://img.shields.io/badge/TM_Cloud_Solutions-Cloud_&_DevSecOps-0284C7?style=flat-square&logo=googlecloud&logoColor=white" alt="TM Cloud Solutions"/>
        <img src="https://img.shields.io/badge/QuickIntell-AI_Intelligence_Platforms-6366F1?style=flat-square&logo=openai&logoColor=white" alt="QuickIntell"/>
        <img src="https://img.shields.io/badge/SentinelForge-Cyber_Defense_Labs-4F46E5?style=flat-square&logo=shield" alt="SentinelForge"/>
      </p>
    </td>
  </tr>
</table>

---

## ⚡ How to Run SentinelForge Properly

SentinelForge supports two execution paradigms: **Local Development Mode** (dual processes for rapid iteration) and **Docker Compose Mode** (production containerization).

### Option 1: Quick Start with Docker Compose (Recommended)

Spins up PostgreSQL 16, Redis 7, the FastAPI Backend, and the React Console with a single command:

```powershell
# 1. Clone the repository
git clone https://github.com/PriyanshuSingh10114/SentinelForge.git
cd SentinelForge

# 2. Configure environment variables (or use defaults)
cp .env.example .env

# 3. Build and launch all containers
docker compose up --build -d

# 4. Verify running health checks
docker compose ps
```

- **Frontend Console**: [http://localhost:3000](http://localhost:3000)
- **Backend Swagger API**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Liveness Probe**: [http://localhost:8000/health](http://localhost:8000/health)
- **Readiness Probe**: [http://localhost:8000/ready](http://localhost:8000/ready)

---

### Option 2: Local Native Development Setup

#### Step 1: Run the Backend (FastAPI + SQLite / Postgres)

```powershell
# Navigate to the backend directory
cd backend

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install all backend requirements
pip install -r requirements.txt

# Run database schema migration & seed default credentials
python -m app.database.init_db

# Start the FastAPI server on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 2: Run the Frontend Console (React + Vite)

Open a new PowerShell terminal:

```powershell
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server with proxy to backend port 8000
npm run dev
```

The console will be accessible at: **`http://localhost:5173`** (or port specified in terminal).

---

### Step 3: Run the Complete Test Suite

Verify all 33 unit, correlation, AI, and OWASP security tests:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -v
```

---

## 🔑 Demo Seed Accounts

> **Notice:** Demo environment with synthetic security data only. Never use production credentials.

| Role | Email | Password | Scope of Authority |
| :--- | :--- | :--- | :--- |
| <img src="https://img.shields.io/badge/ADMIN-7C4DFF?style=flat-square" alt="Admin"/> | `admin@sentinelforge.local` | `SentinelAdmin123!` | Full control: User IAM, Policies, HITL Remediation Approvals |
| <img src="https://img.shields.io/badge/ANALYST-0288D1?style=flat-square" alt="Analyst"/> | `analyst@sentinelforge.local` | `SentinelAnalyst123!` | Incident investigation, AI triage, timeline inspection |
| <img src="https://img.shields.io/badge/DEVELOPER-4F46E5?style=flat-square" alt="Developer"/> | `developer@sentinelforge.local` | `SentinelDev123!` | Artifact scanning, DLP scans, personal finding review |
| <img src="https://img.shields.io/badge/VIEWER-64748B?style=flat-square" alt="Viewer"/> | `viewer@sentinelforge.local` | `SentinelViewer123!` | Read-only security telemetry & dashboards |

---

## 🏗️ High-Level System Architecture

```mermaid
graph TD
    Client["Enterprise Security Console (React 18 + TS + Tailwind)"] -->|HTTPS / WSS| Gateway["FastAPI Edge Gateway"]
    Sources["Cloud Audit / Syslog / AppSec Scanners"] -->|POST /api/v1/events| Gateway

    subgraph Security Backend (FastAPI Core)
        Gateway --> Auth["Bcrypt + JWT Authentication & RBAC Middleware"]
        Auth --> RateLimit["Token-Bucket Rate Limiter (5 Strikes Lockout)"]
        RateLimit --> Normalizer["Event Normalization Engine"]
        Normalizer --> RuleEngine["Deterministic Rule Engine"]
        Normalizer --> DLPEngine["DLP & Shannon Entropy Secret Masking Engine"]
        
        RuleEngine --> CorrelationEngine["Correlation & Risk Scoring Engine (0-100)"]
        DLPEngine --> CorrelationEngine
        CorrelationEngine --> IncidentDB[(PostgreSQL 16 Database)]
    end

    subgraph AI Investigation Subsystem
        IncidentDB --> LangGraphAgent["LangGraph AI Security Investigator"]
        LangGraphAgent --> ReadTools["Controlled Read-Only Inspection Tools"]
        LangGraphAgent --> RAGKB["RBAC-Gated Security Knowledge Base"]
        LangGraphAgent --> OutputValidator["Pydantic Structured Output Validation"]
    end

    subgraph Governance & Human Approval
        OutputValidator --> PendingRemediation["Remediation Action (PENDING_APPROVAL)"]
        PendingRemediation --> AdminGate{"Admin Approval Gate"}
        AdminGate -->|Approve| SimulatedExec["Simulated Remediation Execution"]
        AdminGate -->|Reject / Audit| AuditTrail[(Append-Only Audit Log)]
    end
```

---

## 🛡️ Core Capabilities

- **🔐 Robust Authentication & Deterministic RBAC**: Bcrypt password hashing, short-lived JWT access tokens with rotation (`jti`), progressive 5-strike account lockout freezing repeated brute-force attacks for 15 minutes, and server-side RBAC dependencies (`require_role`, `require_permission`).
- **📥 Normalized Security Telemetry Ingestion**: Universal ingestion API accepting diverse formats (`user`, `username`, `principal` $\rightarrow$ `actor`; `client_ip`, `remote_addr` $\rightarrow$ `source_ip`).
- **🔍 Explainable Risk Scoring (0–100)**: Transparent risk scoring showing exact additive factors (e.g., $+25$ Restricted data, $+20$ Privileged account, $+20$ Repeated failed login).
- **🕵️ Data Classification & DLP Secret Masking**: High-precision regex pattern matchers combined with Shannon entropy heuristics ($H \ge 4.5$ bits/char) detecting AWS keys, GitHub tokens, Slack webhooks, Private keys, JWTs, DB connection strings, and PII. Immediate automated masking (`AKIA****************MPLE`) guarantees zero plaintext secrets in storage or logs.
- **🗺️ STRIDE Threat Modeling Engine**: Architecture decomposition categorizing threats into Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege with lifecycle tracking (`OPEN`, `MITIGATED`, `ACCEPTED`, `FALSE_POSITIVE`).
- **🤖 Controlled LangGraph AI Investigator**: Multi-step state machine orchestrator (`LOAD_INCIDENT` $\rightarrow$ `COLLECT_EVIDENCE` $\rightarrow$ `ANALYZE` $\rightarrow$ `SYNTHESIZE`) equipped exclusively with read-only inspection tools. Fortified against prompt injection with strict context separation envelopes and offline deterministic fallback.
- **🧑‍⚖️ Human-in-the-Loop (HITL) Remediation Gates**: AI recommends remediation; actions enter `PENDING_APPROVAL` status and can strictly only be approved and executed by an Administrator.
- **📜 Tamper-Evident Audit Trail**: Append-only auditing recording actor, action, resource, timestamp, and request ID for all security-sensitive operations.
- **🚀 DevSecOps & Cloud Ready**: Multi-stage Docker containerization (non-root `sentinel`), GitHub Actions pipelines (Bandit SAST, Gitleaks, pip-audit, Trivy), and production Terraform AWS IaC modules.

---

## 📂 Monorepo Structure

```
sentinelforge/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST endpoints (/auth, /events, /incidents, /dlp, /threats, /scans)
│   │   ├── core/            # Config, JSON logging, sanitized error handlers
│   │   ├── models/          # SQLAlchemy relational models
│   │   ├── schemas/         # Strict Pydantic v2 schemas
│   │   ├── security/        # Bcrypt, JWT rotation, server-side RBAC dependencies
│   │   ├── rules/           # Deterministic security rule engine
│   │   ├── dlp/             # Data classification, regex patterns, Shannon entropy masking
│   │   ├── correlation/     # Incident correlation engine & explainable risk scorer
│   │   ├── threat_modeling/ # STRIDE decomposition engine
│   │   ├── ai/              # LangGraph investigator, read-only tools, prompt envelopes, RAG
│   │   └── services/        # Event normalizer, audit logger, investigation service
│   └── tests/               # 33 unit, correlation, AI, and OWASP security tests
├── frontend/                # React 18 + TypeScript + Vite + Tailwind Console
│   └── src/
│       ├── api/             # Typed API client
│       ├── components/      # Enterprise navbar, sidebar, layout
│       └── pages/           # Incidents, Attacks, DLP, Threat Modeling, Scans, IAM, Audit
├── docs/                    # Architecture, Database, Threat Model, ADRs, Security Review
├── docker/                  # Hardened Dockerfiles (backend non-root, frontend Nginx CSP)
├── infra/terraform/         # Modular AWS Infrastructure as Code (VPC, RDS, IAM)
├── .github/workflows/       # CI/CD pipelines (ci.yml, security.yml, deploy.yml)
├── docker-compose.yml       # Local multi-service orchestration
└── README.md
```

---

## 📚 Technical Documentation Index

- 📐 [System Architecture & Invariants](docs/architecture.md)
- 🗄️ [Database Schema & Entity Relationships](docs/database.md)
- 🛡️ [STRIDE Threat Model & Boundaries](docs/threat-model.md)
- 🧠 [AI Security & Prompt Defense Architecture](docs/ai-security.md)
- 🏛️ [Architecture Decision Records (ADR-001 to ADR-007)](docs/decisions.md)
- 🔍 [Comprehensive Security Review](docs/final-security-review.md)
- 🎯 [Technical Interview Talking Points](docs/interview-talking-points.md)

---

<div align="center">
  <sub>Built with precision by <a href="https://github.com/PriyanshuSingh10114"><b>Priyanshu Singh</b></a>. Released under the MIT License.</sub>
</div>
