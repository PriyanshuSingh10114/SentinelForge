from datetime import datetime, timedelta, timezone
import pytest
from httpx import ASGITransport, AsyncClient
from app.correlation.engine import correlate_events_into_incident
from app.database.init_db import init_db
from app.database.session import AsyncSessionLocal
from app.main import app
from app.models.event import SecurityEvent


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


async def get_analyst_token(client: AsyncClient) -> str:
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@sentinelforge.local", "password": "SentinelAnalyst123!"},
    )
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_demo_scenario_1_multi_stage_correlation_and_risk_scoring():
    now = datetime.now(timezone.utc)
    target_user = "developer01"
    target_ip = "198.51.100.77"

    events = []
    # 1. 5 Failed Logins (09:40 to 09:42)
    for i in range(5):
        events.append(
            SecurityEvent(
                event_type="failed_login",
                severity="MEDIUM",
                source="auth_service",
                actor=target_user,
                source_ip=target_ip,
                timestamp=now - timedelta(minutes=30 - i),
                raw_payload={"attempt": i + 1, "reason": "Bad credentials"},
                normalized_payload={},
            )
        )

    # 2. Successful Login (09:43)
    events.append(
        SecurityEvent(
            event_type="login",
            severity="INFO",
            source="auth_service",
            actor=target_user,
            source_ip=target_ip,
            timestamp=now - timedelta(minutes=25),
            raw_payload={"action": "AUTHENTICATE_SUCCESS"},
            normalized_payload={},
        )
    )

    # 3. Privileged Endpoint Access (09:44)
    events.append(
        SecurityEvent(
            event_type="api_request",
            severity="HIGH",
            source="api_gateway",
            actor=target_user,
            source_ip=target_ip,
            timestamp=now - timedelta(minutes=24),
            raw_payload={"action": "UPDATE_POLICY", "resource": "/admin/policies"},
            normalized_payload={},
        )
    )

    # 4. Restricted File Access (09:45)
    events.append(
        SecurityEvent(
            event_type="file_access",
            severity="HIGH",
            source="s3_gateway",
            actor=target_user,
            source_ip=target_ip,
            timestamp=now - timedelta(minutes=23),
            raw_payload={"resource": "customer_pii_vault.parquet", "classification": "RESTRICTED", "action": "DOWNLOAD"},
            normalized_payload={},
        )
    )

    # 5. DLP Secret Trigger (09:46)
    events.append(
        SecurityEvent(
            event_type="dlp_violation",
            severity="CRITICAL",
            source="dlp_engine",
            actor=target_user,
            source_ip=target_ip,
            timestamp=now - timedelta(minutes=22),
            raw_payload={"matched_pattern": "AKIA****************MPLE", "data_type": "AWS_ACCESS_KEY"},
            normalized_payload={},
        )
    )

    async with AsyncSessionLocal() as session:
        for e in events:
            session.add(e)
        await session.commit()
        for e in events:
            await session.refresh(e)

        # Correlate all events
        incident = await correlate_events_into_incident(
            db=session,
            events=events,
            title="Potential Account Compromise with Exfiltration",
            description="Multi-stage credential stuffing followed by privileged API invocation and restricted data access.",
        )

        incident_id = incident.id
        incident_number = incident.incident_number

        # Check Risk Scoring: must be explainable and >= 80 (HIGH or CRITICAL)
        assert incident.risk_score >= 80
        assert incident.severity in ("HIGH", "CRITICAL")
        assert len(incident.risk_factors) >= 4

        reasons = [f["reason"] for f in incident.risk_factors]
        assert any("Restricted or confidential data" in r for r in reasons)
        assert any("Administrative or privileged" in r for r in reasons)
        assert any("Repeated failed authentication" in r for r in reasons)
        assert any("Unmasked credentials or secrets" in r for r in reasons)

    # Now verify through API
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_analyst_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch Incident Detail
        detail_res = await client.get(f"/api/v1/incidents/{incident_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["incident_number"] == incident_number
        assert detail["events_count"] == 9
        assert target_user in detail["affected_users"]
        assert "customer_pii_vault.parquet" in detail["affected_assets"]

        # Timeline verification: chronological order
        timeline = detail["timeline"]
        assert len(timeline) == 9
        assert timeline[0]["event_type"] == "failed_login"
        assert timeline[-1]["event_type"] == "dlp_violation"

        # 2. Fetch Attack Graph
        graph_res = await client.get(f"/api/v1/incidents/{incident_id}/attack-graph", headers=headers)
        assert graph_res.status_code == 200
        graph = graph_res.json()
        assert len(graph["nodes"]) >= 3
        node_types = {n["type"] for n in graph["nodes"]}
        assert {"INCIDENT", "USER", "ASSET"}.issubset(node_types)
        assert len(graph["edges"]) >= 3

        # 3. Update Incident Status
        patch_res = await client.patch(
            f"/api/v1/incidents/{incident_id}/status",
            json={"status": "INVESTIGATING"},
            headers=headers,
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "INVESTIGATING"
