# SentinelForge — Complete Static Data & Data-Integrity Audit

**Audit Date:** November 2026  
**Auditor:** Senior Full-Stack Engineer, Cybersecurity Architect, and SOC Platform Lead  
**Document Purpose:** Systematic inventory and classification of all static, hardcoded, fabricated, and configuration data across the SentinelForge codebase.

---

## 1. Master Static Data Inventory & Classification Matrix

| File Path | Component / Module | Data / Metric | Classification | Operational Impact | Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `frontend/src/pages/DashboardPage.tsx` | Dashboard Velocity Chart | `telemetryTrend` array (`14:00` - `20:00` event points: 12, 19, 28, 45, 32, 58, 42) | **Fabricated / Fake Telemetry** | Displays artificial hourly event frequencies and anomaly counts even when zero events have been ingested into the database. | **REPLACE** with dynamic temporal aggregation computed from actual database events; show an honest empty state when no events exist. |
| `frontend/src/pages/DashboardPage.tsx` | Operational Metrics Card | Mean Time to Investigate (MTTI): `2.4 min` | **Fabricated / Hardcoded Metric** | Claims a static 2.4-minute SLA without calculating actual incident detection-to-resolution intervals from database records. | **REPLACE** with dynamically calculated average resolution time from resolved/closed incidents, or display `"N/A (No resolved incidents)"`. |
| `frontend/src/pages/DashboardPage.tsx` | Operational Metrics Card | Human Approval Gate Status: `100% Gated` | **Fabricated / Hardcoded Metric** | Hardcoded visual placeholder that does not query actual remediation action statuses from the backend. | **REPLACE** with dynamic calculation querying `api.remediations.list()` showing actual pending vs executed actions. |
| `frontend/src/pages/ScansPage.tsx` | DevSecOps Scans Page | `DEMO_SCAN_FINDINGS` array (4 static scan records: Bandit, pip-audit, trivy, gitleaks) | **Hardcoded Mock Dataset** | Disconnects the UI from backend endpoints `GET /api/v1/scans/findings` and `POST /api/v1/scans/ingest`; changes are never persisted. | **REPLACE** by connecting to `api.scans.findings()`; render actual database findings with an honest empty state and on-demand demo ingestion action. |
| `frontend/src/api/client.ts` | API Client Service | Missing `api.scans` methods | **Disconnected Integration** | Scans backend endpoints exist in `backend/app/api/v1/scans.py` but cannot be invoked by the React frontend. | **CONNECT** by adding `api.scans.findings()` and `api.scans.ingest()` to `client.ts`. |
| `frontend/src/pages/DlpPage.tsx` | Interactive DLP Scanner | `DEMO_PAYLOADS` array (AWS keys, DB URI, PII, Clean config) | **Legitimate Test Fixture / Preset** | Provides sample payloads for analysts to click and test DLP regex and Shannon entropy algorithms; does not claim to be persisted operational records. | **PRESERVE & LABEL** explicitly as "Test Input Presets". |
| `frontend/src/pages/LoginPage.tsx` | Login Authentication Page | `DEMO_PRESETS` array (Admin, Analyst, Developer, Viewer credentials) | **Legitimate Reference Data** | Maps to actual seeded users in `init_db.py`; enables rapid role-switching during technical demonstrations. | **PRESERVE** as authenticated credential presets. |
| `backend/app/database/init_db.py` | Baseline DB Seeding | Roles, Permissions, Classifications, Baseline Assets, Users, Baseline Policies | **Legitimate Baseline Configuration** | Required foundation for RBAC enforcement, data classification weights, and system operation. | **PRESERVE**; does not contain fake operational events or fabricated incidents. |
| `backend/app/rules/definitions.py` | Rule Engine | Detection thresholds (e.g. 5 failed logins within 10 minutes) | **Legitimate Security Configuration** | Mathematical parameters defining threat triggering conditions for brute force and privilege escalation. | **PRESERVE**. |
| `backend/app/core/config.py` | Pydantic Settings | Default timeouts, algorithms, rate limits, CORS origins | **Legitimate Application Configuration** | Environment defaults necessary for runtime operation. | **PRESERVE**. |
| `backend/tests/*` | Pytest Automated Test Suite | Test fixtures, sample security events, mock LLM outputs | **Test Fixtures** | Isolated test fixtures used exclusively during CI/CD test execution; never rendered in the live application. | **PRESERVE & SEPARATE**. |

---

## 2. Classification Summary

- **Total Inspected Files:** 86
- **Unnecessary Fabricated Data (Category A):** 4 items (Dashboard synthetic trend array, MTTI hardcoded statistic, Human Gate hardcoded string, Scans static mock array).
- **Legitimate Application Configuration (Category B):** 4 items (Detection rules, baseline RBAC roles, data classifications, Pydantic settings).
- **Test Fixtures & Presets (Category C):** 2 items (Pytest fixtures, DLP scanner test presets).
- **Legitimate Reference Data (Category D):** 1 item (Seeded demo authentication presets).

---

## 3. Remediation Strategy

1. **Dashboard Time-Series:** Dynamically bucket actual event timestamps from `api.events.list()` into hourly buckets. If no events exist, render an honest empty state informing the user that no telemetry has been recorded yet.
2. **Dashboard Operational Metrics:** Calculate real MTTI from resolved incidents (`resolved_at - detected_at`). Calculate Human Approval Gate metrics from `api.remediations.list()`.
3. **Scans Page Integration:** Connect `ScansPage.tsx` to `GET /api/v1/scans/findings`. Provide an on-demand "Simulate Security Scan" button that uses `POST /api/v1/scans/ingest` with explicit simulation provenance metadata.
4. **Simulation Provenance:** Ensure any generated demonstration telemetry is explicitly tagged with `source_type = "simulated"` and displayed with a `[SIMULATED]` provenance badge in the UI.

