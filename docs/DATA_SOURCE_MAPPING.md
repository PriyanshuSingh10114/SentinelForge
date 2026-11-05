# SentinelForge — Complete Frontend-to-Backend Data Source Mapping

**Document Version:** 1.0  
**Verification Date:** November 2026  
**Auditor:** Senior Full-Stack Engineer & DevSecOps Architect

---

## 1. Architectural End-to-End Metric Tracing Matrix

This document maps every metric and dataset displayed across the SentinelForge console to its exact backend API endpoint, business service layer, SQLAlchemy query, and database table.

```
+--------------------------------------------------------------------------------------------------------------------------+
|                                              END-TO-END DATA TRACEABILITY                                                |
|  Frontend Component       API Endpoint                    Backend Service         Database Query         Source Data     |
|  -------------------      ----------------------------    --------------------    --------------------   ------------    |
|  Total Telemetry Ingest   GET /api/v1/events?limit=100    event_service.py        SELECT count(id)...    security_events |
|  Active Incidents Count   GET /api/v1/incidents           incidents.py            SELECT * FROM inc...   incidents       |
|  Critical Incidents       GET /api/v1/incidents?sev=CRIT  incidents.py            WHERE severity='CRIT'  incidents       |
|  DLP Interceptions Count  GET /api/v1/dlp/findings        dlp.py                  SELECT * FROM dlp...   dlp_findings    |
|  Telemetry Velocity Chart GET /api/v1/events?limit=100    event_service.py        Timestamp bucket eval  security_events |
|  Mean Time to Investigate GET /api/v1/incidents           incidents.py            resolved_at - det_at   incidents       |
|  Human Approval Gate Stat GET /api/v1/remediations        remediations.py         SELECT * FROM rem...   remediations    |
|  DevSecOps Scan Findings  GET /api/v1/scans/findings      scans.py                SELECT * FROM scan...  scan_findings   |
|  STRIDE Threat Models     GET /api/v1/threat-models       threats.py              SELECT * FROM threat.. threat_models   |
|  Audit Trail Ledger       GET /api/v1/admin/audit-logs    audit_service.py        SELECT * FROM audit... audit_logs      |
|  User & IAM Directory     GET /api/v1/admin/users         admin.py                SELECT * FROM users... users           |
|  Security Policies List   GET /api/v1/admin/policies      admin.py                SELECT * FROM policy.. security_policies|
+--------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Granular Metric Tracing Specifications

### A. Dashboard Metrics & Telemetry
- **Total Ingested Events:**
  - **Frontend:** `DashboardPage.tsx` (`eventsCount`)
  - **API Client:** `api.events.list({ limit: 100 })`
  - **Backend Endpoint:** `GET /api/v1/events` (`backend/app/api/v1/events.py:64`)
  - **Service Function:** `search_security_events()` (`backend/app/services/event_service.py:59`)
  - **Database Query:** `SELECT count(security_events.id) FROM security_events`
  - **Actual Data:** Integer count of all persisted security events. Empty database yields `0`.

- **Event Telemetry Velocity & Anomaly Trends (Chart):**
  - **Frontend:** `DashboardPage.tsx` (`AreaChart data={telemetryTrend}`)
  - **API Client:** `api.events.list({ limit: 100 })`
  - **Backend Endpoint:** `GET /api/v1/events`
  - **Processing Logic:** Chronological bucketing of `timestamp` fields from persisted records into hourly intervals, counting events and anomalies (`severity in ('CRITICAL', 'HIGH')`).
  - **Empty State:** If 0 events exist, displays an empty state explaining that event telemetry has not yet been ingested.

- **Critical & High Severity Incidents:**
  - **Frontend:** `DashboardPage.tsx` (`criticalCount`, `highCount`)
  - **API Client:** `api.incidents.list()`
  - **Backend Endpoint:** `GET /api/v1/incidents` (`backend/app/api/v1/incidents.py:29`)
  - **Database Query:** `SELECT * FROM incidents ORDER BY detected_at DESC`
  - **Actual Data:** Filtered from real database incident records.

- **Mean Time to Investigate (MTTI):**
  - **Frontend:** `DashboardPage.tsx` (`mttiValue`, `mttiSub`)
  - **API Client:** `api.incidents.list()`
  - **Computation:** Computes average interval: `(resolved_at - detected_at)` across resolved/closed incidents.
  - **Empty State:** When no resolved incidents exist, displays `N/A` with subtitle `No closed incidents in database`.

- **Human Approval Gate Status:**
  - **Frontend:** `DashboardPage.tsx` (`gateValue`, `gateSub`)
  - **API Client:** `api.remediations.list()`
  - **Backend Endpoint:** `GET /api/v1/remediations` (`backend/app/api/v1/remediations.py`)
  - **Database Query:** `SELECT * FROM remediation_actions`
  - **Actual Data:** Displays count of `PENDING_APPROVAL` vs `EXECUTED` actions.

---

### B. DevSecOps & Security Scans
- **Findings Inventory & Summary Cards:**
  - **Frontend:** `ScansPage.tsx` (`findings`)
  - **API Client:** `api.scans.findings()`
  - **Backend Endpoint:** `GET /api/v1/scans/findings` (`backend/app/api/v1/scans.py:41`)
  - **Database Query:** `SELECT * FROM scan_findings ORDER BY created_at DESC`
  - **Empty State:** Honest empty state indicating no scans have been ingested, with a dedicated "Simulate DevSecOps Scan Findings" button.

---

### C. Security Event Telemetry & Simulation Provenance
- **Telemetry Stream & Provenance Badges:**
  - **Frontend:** `EventsPage.tsx` (`events`)
  - **API Client:** `api.events.list()`
  - **Backend Endpoint:** `GET /api/v1/events`
  - **Provenance Calculation:** Checks `source === 'simulated_generator'` or `normalized_payload.is_simulated === true`.
  - **Display:** Tags events with `[SIMULATED]` or `[LIVE]`.

- **Controlled Event Simulation:**
  - **Frontend:** `EventsPage.tsx` (`Generate Demo Events` button)
  - **API Client:** `api.events.simulate()`
  - **Backend Endpoint:** `POST /api/v1/events/simulate` (`backend/app/api/v1/events.py:92`)
  - **Database Action:** Inserts controlled demonstration events with explicit metadata into `security_events`.

