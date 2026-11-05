# SentinelForge — Operational Runbook & Local Execution Guide

**Environment:** Windows 10 / 11 (PowerShell)  
**Backend:** Python 3.12+ (FastAPI, SQLAlchemy, LangGraph)  
**Frontend:** Node.js 18+ / npm (React, Vite, Tailwind CSS Light Mode)  
**Database:** SQLite (`sentinelforge_dev.db`) for local testing; PostgreSQL 16 for containerized production

---

## 1. Quick-Start Commands (Windows PowerShell)

Open two PowerShell windows in `e:\React Projects\SentinelForge`.

### Terminal 1: Backend Setup & Execution

```powershell
# 1. Set working directory to project root
cd "e:\React Projects\SentinelForge"

# 2. Configure Python Path and Environment Variables
$env:PYTHONPATH = "backend"
$env:JWT_SECRET = "super-secret-sentinelforge-dev-key-honeywell-demo-32chars"
$env:DATABASE_URL = "sqlite+aiosqlite:///./sentinelforge_dev.db"
$env:DEBUG = "True"

# 3. Initialize and Seed the Database with Demo Scenarios & Users
python -m app.database.init_db

# 4. Start the FastAPI Application Gateway
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

*Expected Terminal 1 Output:*
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

---

### Terminal 2: Frontend Setup & Execution

```powershell
# 1. Set working directory to project root
cd "e:\React Projects\SentinelForge"

# 2. Install dependencies (if not already installed)
npm install --prefix frontend

# 3. Start the Vite React Development Server
npm run dev --prefix frontend
```

*Expected Terminal 2 Output:*
```
  VITE v5.4.21  ready in 450 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## 2. Test Execution & Verification

Run the full automated test suite (36 tests) across all functional domains:

```powershell
cd "e:\React Projects\SentinelForge"
$env:PYTHONPATH = "backend"
pytest backend/tests -v
```

*Expected Verification Output:*
```
======================= 36 passed in ~12.5s =======================
```

---

## 3. Demo Credentials & Access Points

| Role | Email Address | Password | Permissions & Access Scope |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@sentinelforge.local` | `AdminPass123!` | Full platform control: User provisioning, policy editing, incident status, remediation. |
| **Analyst** *(Recommended for Demo)* | `analyst@sentinelforge.local` | `AnalystPass123!` | Security operations: Run AI investigations, approve remediations, DLP scans, threat modeling. |
| **Developer** | `developer@sentinelforge.local` | `DeveloperPass123!` | DevSecOps scope: Ingest vulnerability scans, inspect code findings, read security events. |
| **Viewer** | `viewer@sentinelforge.local` | `ViewerPass123!` | Read-only executive dashboard: Read incidents and overview metrics; all mutations blocked. |

### Key URLs:
- **Web Application Console:** `http://localhost:5173`
- **FastAPI OpenAPI Documentation:** `http://127.0.0.1:8000/docs`
- **Backend Health Check:** `http://127.0.0.1:8000/api/v1/health`
- **Backend Readiness Check:** `http://127.0.0.1:8000/api/v1/health/ready`

---

## 4. Reset & Disaster Recovery Procedures

### Reset Database to Clean State
If data becomes cluttered during test runs or demonstrations:

```powershell
cd "e:\React Projects\SentinelForge"
# Remove SQLite database file
if (Test-Path "sentinelforge_dev.db") { Remove-Item "sentinelforge_dev.db" -Force }

# Re-run database seeding script
$env:PYTHONPATH = "backend"
python -m app.database.init_db
```

### Port Conflict Recovery
If port 8000 or 5173 is already occupied:

```powershell
# Find and terminate process on port 8000
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Find and terminate process on port 5173
Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

---

## 5. Docker Containerized Execution (Alternative)

To run the complete platform inside multi-container Docker Compose:

```powershell
cd "e:\React Projects\SentinelForge"

# Build and start PostgreSQL, Backend API, and Frontend Console
docker compose up --build -d

# Verify container statuses and healthchecks
docker compose ps
```

