# SentinelForge — Dashboard Metrics Reference & Mathematical Specification

**Document Version:** 1.0  
**Purpose:** Mathematical definition, data provenance, and behavioral reference for all metrics displayed on the SentinelForge SecOps Posture Dashboard.

---

## 1. Posture Dashboard Metrics Matrix

| Metric Name | Display Location | Mathematical / Logical Definition | Data Source Table & Field | Zero / Empty Database State |
| :--- | :--- | :--- | :--- | :--- |
| **Organization Security Posture** | Top Banner | $\text{Score} = 100$ (if no threats) else $\max(30, 100 - 18 \cdot N_{\text{crit}} - 8 \cdot N_{\text{high}} - \min(20, 3 \cdot N_{\text{dlp}}))$ | `incidents` (severity), `dlp_findings` | `100 / 100` (`SECURE`) with subtitle *"Baseline — No active threats or incidents"* |
| **Critical Incidents** | Top Card 2 | $N_{\text{crit}} = \sum [ \text{severity} = \text{'CRITICAL'} ]$ | `incidents.severity` | `0` with subtitle *"Requiring immediate containment"* |
| **High Severity Incidents** | Top Card 3 | $N_{\text{high}} = \sum [ \text{severity} = \text{'HIGH'} ]$ | `incidents.severity` | `0` with subtitle *"Investigating via AI orchestrator"* |
| **DLP Interceptions** | Top Card 4 | $N_{\text{dlp}} = \text{Count}(\text{dlp\_findings})$ | `dlp_findings.id` | `0` with subtitle *"Credentials & PII masked in transit"* |
| **Telemetry Velocity & Anomaly Trends** | Main Chart (Area) | Grouped count of events and anomalies by hourly intervals: $V(t) = \text{Count}(\text{events}_t)$, $A(t) = \text{Count}(\text{anomalies}_t)$ | `security_events.timestamp`, `security_events.severity` | Renders clean empty state: *"No Telemetry Timestamps Recorded — Ingest security events to visualize trends."* |
| **Mean Time to Investigate (MTTI)** | Operational Metrics | $\text{MTTI} = \frac{1}{K} \sum_{k=1}^{K} (t_{\text{resolved}, k} - t_{\text{detected}, k})$ for resolved incidents | `incidents.detected_at`, `incidents.resolved_at`, `incidents.status` | Displays `"N/A"` with subtitle *"No closed incidents in database"* |
| **Human Approval Gate Status** | Operational Metrics | Displays $N_{\text{pending}}$ and $N_{\text{executed}}$ from database remediation records | `remediation_actions.status` | Displays `"0 Pending Actions"` with subtitle *"Zero unreviewed actions"* |
| **Total Ingested Telemetry** | Operational Metrics | $\text{Total} = \text{Count}(\text{security\_events})$ | `security_events.id` | Displays `"0 Events"` with subtitle *"Persisted in database ledger"* |
| **Active Correlated Incidents** | Bottom Table | Query `incidents` ordered by `detected_at DESC` limit 5 | `incidents` table | Displays *"No active incidents detected. Ingest security events to observe automatic correlation."* |

---

## 2. Dynamic Fallback and Error Handling

1. **API Error Isolation:** If any individual API call fails during dashboard loading (e.g., remediations endpoint unreachable), the dashboard catches the exception individually, logs it, and falls back to an explicit empty state rather than fabricating placeholder numbers.
2. **Zero-Record Honesty:** An empty database strictly yields zeros and honest empty states. The application never invents sample events (e.g. `1,248 events`) to appear populated.
3. **Tooltip Theming:** Chart tooltips utilize clean light mode styling (`#ffffff` background, `#e2e8f0` border, `#0f172a` typography) ensuring high contrast and readability.

