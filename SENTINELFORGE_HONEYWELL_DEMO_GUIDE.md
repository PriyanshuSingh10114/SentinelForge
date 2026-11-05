# SentinelForge — Honeywell Interview Demonstration Guide

**Target Role:** Cybersecurity Engineering & AI Intern — Honeywell  
**Target Timeframe:** 5 to 7 Minutes  
**Theme:** Autonomous Threat Defense, Safety-Critical AI Systems, and Enterprise DevSecOps  
**UI Setting:** Enterprise High-Contrast Light Mode

---

## 1. Executive Demonstration Philosophy

Honeywell develops safety-critical automation, aerospace avionics, building technologies, and industrial cybersecurity solutions (Forge Cybersecurity Suite). In an interview with Honeywell engineering leaders, prioritize:
1. **Determinism over Stochasticity:** Show how SentinelForge guarantees zero-hallucination AI through structured LangGraph state machines and deterministic safety fallbacks.
2. **Safety-Critical Guardrails (Human-in-the-Loop):** Emphasize that autonomous agents **never** execute destructive actions (like network isolation or credential revocation) without authenticated human approval.
3. **Data Loss Prevention & Mathematical Rigor:** Highlight the Shannon entropy detection engine for catching cryptographic keys and firmware credentials before they leak.
4. **End-to-End Traceability:** Show full MITRE ATT&CK mapping, STRIDE threat modeling, and immutable audit logging.

---

## 2. Minute-by-Minute Demonstration Script (5–7 Minutes)

```
0:00 - 1:00  [The Hook & Enterprise Context]
             "The challenge of modern SOCs: alert fatigue, disjointed telemetry, and uncontrolled AI."
             Action: Log into SentinelForge Console as Security Analyst.

1:00 - 2:00  [Telemetry Ingestion & Deterministic Rule Engine]
             "Normalizing heterogeneous cloud and industrial telemetry into unified schemas."
             Action: Show Ingestion Feed -> View AWS CloudTrail & Syslog events.

2:00 - 3:00  [Temporal Correlation & Dynamic Risk Scoring]
             "Correlating discrete alerts into an attack chain with mathematical risk decay."
             Action: Open Incident Queue -> Select Incident #1 -> Inspect Attack Chain & Risk 88.5.

3:00 - 4:30  [Autonomous AI Investigation & MITRE ATT&CK Mapping]
             "LangGraph 5-node autonomous agent: Zero hallucination, deterministic safety fallback."
             Action: Click 'Run AI Investigation' -> Watch real-time execution -> Review findings.

4:30 - 5:30  [Human-in-the-Loop (HITL) Safety Gate & Remediation]
             "The Honeywell safety principle: Autonomous analysis, human authorization."
             Action: Review proposed 'Quarantine Host' action -> Click 'Approve & Execute'.

5:30 - 6:30  [DLP Shannon Entropy Engine & DevSecOps Posture]
             "Mathematical information theory preventing credential leakage ($H \ge 4.5$)."
             Action: Run DLP Scan on sample payload containing AWS key and high-entropy secret.

6:30 - 7:00  [Conclusion & Architecture Defense]
             "Production-ready: 36/36 tests passing, OWASP Top 10 hardened, Docker & CI/CD ready."
             Action: Show STRIDE Canvas or Admin Governance page.
```

---

## 3. Detailed Walkthrough & Scripted Dialogues

### Minute 0:00 – 1:00 | The Hook & Enterprise Context
- **Screen:** Navigate to `http://localhost:5173/login`.
- **Action:** Enter `analyst@sentinelforge.local` and `AnalystPass123!`. Click **Sign In**.
- **Dialogue:**
  > *"Good morning/afternoon. Today I want to walk you through SentinelForge, an autonomous security operations and threat defense platform I built to solve two of the biggest problems facing modern industrial and enterprise SOCs: alert fatigue and unverified AI outputs.*
  >
  > *In high-assurance environments like Honeywell's industrial automation systems, security teams process millions of logs daily. Many teams try to bolt on LLMs, but uncontrolled LLMs introduce hallucinations, prompt injection vulnerabilities, and unpredictable actions. SentinelForge couples deterministic rule-based correlation and Shannon-entropy DLP with a 5-node LangGraph autonomous agent that operates under strict Human-in-the-Loop safety guardrails."*

### Minute 1:00 – 2:00 | Telemetry Ingestion & Threat Detection
- **Screen:** Navigate to **Events** (`/events`).
- **Action:** Show the normalized events table. Point out heterogeneous sources (`aws_cloudtrail`, `auth_service`, `s3_storage`).
- **Dialogue:**
  > *"Our pipeline ingests multi-source telemetry—from cloud audit trails to industrial Syslog streams. Ingestion normalizes timestamps into ISO-8601 UTC, extracts actor principals, and categorizes severity.*
  >
  > *Here, our deterministic rule engine evaluated five failed logins within a three-minute window, followed by an unauthorized IAM role attachment. Rather than flooding the analyst with ten disconnected alerts, our correlation engine links them."*

### Minute 2:00 – 3:00 | Temporal Correlation & Dynamic Risk Scoring
- **Screen:** Navigate to **Incidents** (`/incidents`), click on the active High/Critical incident.
- **Action:** Point out the **Risk Gauge (88.5 / 100)** and the **Attack Chain Timeline**.
- **Dialogue:**
  > *"This is the correlated incident. Rather than relying on static severity tags, SentinelForge calculates a dynamic composite risk score: taking event severity weights, scaling by target asset criticality, and applying an exponential temporal decay function.*
  >
  > *The graph visualizes the attacker's trajectory across the MITRE ATT&CK framework: from Initial Access via credential stuffing, to Privilege Escalation, to S3 Data Access."*

### Minute 3:00 – 4:30 | Autonomous AI Investigation (LangGraph StateGraph)
- **Screen:** On the Incident Detail view, click the **"Run AI Investigation"** button.
- **Action:** Watch the status update to *Investigating* and populate the structured report in ~1.5 seconds.
- **Dialogue:**
  > *"Now I'll trigger the autonomous investigator. Under the hood, this runs a 5-node LangGraph state machine: correlating recent telemetry, evaluating MITRE attack stages, querying our internal RAG playbooks, synthesizing evidence, and formulating remediation actions.*
  >
  > *Crucially for safety-critical environments, SentinelForge features a zero-key deterministic fallback. If external AI APIs are unreachable or restricted in air-gapped industrial OT networks, the system autonomously synthesizes a deterministic report using verified graph relationships. Zero hallucinations, zero data leaving the network."*

### Minute 4:30 – 5:30 | Human-in-the-Loop (HITL) Safety Gate
- **Screen:** Scroll down to the **Remediation Plan** section in the Incident view.
- **Action:** Show the proposed action: `QUARANTINE_HOST` (IP: `10.0.0.99`) with status `PENDING_APPROVAL`. Click **"Approve & Execute"**.
- **Dialogue:**
  > *"Notice that the agent did NOT shut down the host autonomously. In industrial systems, shutting down a controller or workstation unexpectedly can disrupt critical operations. SentinelForge enforces a Human-in-the-Loop safety gate.*
  >
  > *Remediations remain in a PENDING status until an authenticated analyst reviews the forensic justification and authorizes execution. Once approved, it executes, updates the incident lifecycle to CONTAINED, and writes an immutable record to our tamper-evident audit ledger."*

### Minute 5:30 – 6:30 | Shannon Entropy DLP & Secret Masking
- **Screen:** Navigate to **DLP Scanner** (`/dlp`).
- **Action:** Paste the demo payload into the scanner and click **Scan Content**:
  ```
  Alert: Deployment script leaked AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE and staging token=dGVzdF9zZWNyZXRfa2V5XzEyMzQ1Njc4OTA=
  ```
- **Dialogue:**
  > *"Data loss prevention is critical in preventing intellectual property and credentials from leaking into public logs or AI models. Our DLP engine uses a dual approach:*
  >
  > *First, strict regular expressions match known credential formats like AWS access keys, immediately blocking them. Second, for unknown tokens, we compute the Shannon entropy: $H(X) = -\sum P(x_i) \log_2 P(x_i)$. Strings with entropy above 4.5 indicate high randomness characteristic of private keys and hashed secrets. As you see here, the AWS key is blocked and the secret token is masked."*

### Minute 6:30 – 7:00 | Conclusion & Architecture Defense
- **Screen:** Navigate to **Threat Modeling** (`/threats`) or show the clean Light Mode **Dashboard**.
- **Dialogue:**
  > *"To ensure enterprise robustness, SentinelForge was built with DevSecOps best practices: 36 automated unit and integration tests passing with 100% code integrity, OWASP Top 10 API security controls enforcing strict server-side RBAC and account lockout, non-root Docker containers, and a high-contrast enterprise light interface.*
  >
  > *Thank you, and I look forward to your questions on our architecture, threat correlation algorithms, or AI safety guardrails."*

---

## 4. Anticipated Interviewer Questions & Instant Defense Answers

### Q1: "How do you prevent the AI agent from hallucinating false security recommendations?"
- **Answer:** *"We use two architectural controls. First, the LangGraph agent uses strict typed schemas (Pydantic models) constraining inputs and outputs. Second, we implement a deterministic synthesis fallback in `app/ai/agent.py`. It constructs findings strictly from SQL telemetry and MITRE ATT&CK rule matches. No unsubstantiated claims can enter the output."*

### Q2: "Why use Shannon Entropy instead of just standard regex patterns in the DLP engine?"
- **Answer:** *"Regex only catches known formats like AWS keys (`AKIA...`) or GitHub tokens (`ghp_...`). It fails on custom API keys, base64-encoded bearer tokens, or proprietary firmware secrets. Shannon entropy measures informational uncertainty. Cryptographic secrets have near-maximum entropy ($\ge 4.5$), allowing us to detect zero-day credential leaks regardless of prefix."*

### Q3: "What prevents a malicious user from modifying incident statuses or threat mitigations?"
- **Answer:** *"We remediated this as an OWASP API1 (BOLA) vulnerability. In `backend/app/api/v1/incidents.py` and `threats.py`, all state mutations require `require_role('Admin', 'Analyst')`. Viewer and Developer roles receive an HTTP 403 Forbidden with security audit logging."*

