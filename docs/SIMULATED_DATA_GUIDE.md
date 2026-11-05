# SentinelForge — Simulated Data & Demonstration Provenance Guide

**Document Version:** 1.0  
**Purpose:** Architecture, schema conventions, and operational procedures for generating, identifying, and managing simulated demonstration data in SentinelForge.

---

## 1. Simulation Philosophy

In high-assurance security engineering, **simulated data must never be presented as genuine live production telemetry**. At the same time, technical demonstrations and automated verification require predictable, reproducible security event patterns (e.g. brute force bursts, IAM privilege escalation attempts).

SentinelForge reconciles these requirements through **Explicit Demonstration Provenance**:
1. **Deliberate User Activation:** Simulated data is never automatically created during application startup. It requires an explicit user action (e.g., clicking **"Generate Demo Events"** or **"Simulate DevSecOps Scan Findings"**).
2. **Provenance Metadata:** Every simulated record carries immutable metadata fields identifying its source.
3. **Visual Tagging:** The user interface prominently displays `[SIMULATED]` badges on demonstration telemetry, distinguishing it from `[LIVE]` telemetry.

---

## 2. Metadata Standards & Database Fields

### A. Simulated Security Events
When generated via `POST /api/v1/events/simulate`, events persist with:
- **`source`:** `"simulated_generator"`
- **`raw_payload`:**
  ```json
  {
    "is_simulated": true,
    "simulation_source": "demo_generator",
    "attempt": 1
  }
  ```
- **`normalized_payload`:**
  ```json
  {
    "is_simulated": true,
    "source_type": "simulated",
    "description": "Simulated brute force attempt"
  }
  ```

### B. UI Provenance Indicators
In `EventsPage.tsx`:
- **`[SIMULATED]` Badge:** Rendered with an amber corporate badge (`bg-amber-50 text-amber-800 border-amber-200`) when `e.source === 'simulated_generator'` or `e.raw_payload.is_simulated === true`.
- **`[LIVE]` Badge:** Rendered with a green corporate badge (`bg-emerald-50 text-emerald-700 border-emerald-200`) for genuine external or API-ingested telemetry.

---

## 3. How to Trigger Controlled Simulations

### Option 1: Via the Web Console
1. Navigate to **Event Telemetry** (`/events`).
2. Click the amber button **"Generate Demo Events"**.
3. Three correlated security events (2 failed logins + 1 IAM privilege escalation) are ingested, tagged as simulated, and correlated into an incident.

### Option 2: Via REST API
```bash
curl -X POST http://127.0.0.1:8000/api/v1/events/simulate \
  -H "Authorization: Bearer <ANALYST_TOKEN>"
```

### Option 3: DevSecOps Scans Simulation
1. Navigate to **AppSec Scans** (`/scans`).
2. If empty, click **"Simulate DevSecOps Scan Findings"**.
3. Three scan findings (Bandit SAST, Trivy Container, Pip-Audit SCA) are ingested into the database via `POST /api/v1/scans/ingest`.

