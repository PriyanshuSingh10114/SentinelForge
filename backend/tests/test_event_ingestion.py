import pytest
from httpx import ASGITransport, AsyncClient
from app.database.init_db import init_db
from app.main import app


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
async def test_event_normalization_across_heterogeneous_sources():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_analyst_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Source A: uses "user" and "client_ip"
        event_a = {
            "user": "developer_alpha",
            "event_type": "file_access",
            "client_ip": "10.0.0.15",
            "severity": "HIGH",
            "resource": "confidential_payroll.csv",
        }
        res_a = await client.post("/api/v1/events", json=event_a, headers=headers)
        assert res_a.status_code == 201
        data_a = res_a.json()
        assert data_a["actor"] == "developer_alpha"
        assert data_a["source_ip"] == "10.0.0.15"
        assert data_a["severity"] == "HIGH"
        assert data_a["event_type"] == "file_access"

        # Source B: uses "username" and "remote_addr"
        event_b = {
            "username": "developer_beta",
            "type": "api_request",
            "remote_addr": "192.168.1.50",
            "level": "CRITICAL",
        }
        res_b = await client.post("/api/v1/events", json=event_b, headers=headers)
        assert res_b.status_code == 201
        data_b = res_b.json()
        assert data_b["actor"] == "developer_beta"
        assert data_b["source_ip"] == "192.168.1.50"
        assert data_b["severity"] == "CRITICAL"
        assert data_b["event_type"] == "api_request"

        # Source C: uses "principal" and "ip"
        event_c = {
            "principal": "developer_gamma",
            "action_type": "privilege_escalation_attempt",
            "ip": "172.16.0.4",
            "severity": "HIGH",
        }
        res_c = await client.post("/api/v1/events", json=event_c, headers=headers)
        assert res_c.status_code == 201
        data_c = res_c.json()
        assert data_c["actor"] == "developer_gamma"
        assert data_c["source_ip"] == "172.16.0.4"
        assert data_c["severity"] == "HIGH"


@pytest.mark.asyncio
async def test_batch_event_ingestion_and_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_analyst_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        batch_payload = {
            "events": [
                {
                    "user": "batch_user_1",
                    "event_type": "failed_login",
                    "severity": "MEDIUM",
                    "ip": "10.10.10.1",
                },
                {
                    "user": "batch_user_2",
                    "event_type": "failed_login",
                    "severity": "CRITICAL",
                    "ip": "10.10.10.2",
                },
                {
                    "user": "batch_user_1",
                    "event_type": "login",
                    "severity": "INFO",
                    "ip": "10.10.10.1",
                },
            ]
        }

        res_batch = await client.post("/api/v1/events/batch", json=batch_payload, headers=headers)
        assert res_batch.status_code == 201
        batch_res = res_batch.json()
        assert len(batch_res) == 3

        # Search filtered by actor="batch_user_1"
        res_search_actor = await client.get("/api/v1/events?actor=batch_user_1", headers=headers)
        assert res_search_actor.status_code == 200
        search_data = res_search_actor.json()
        assert search_data["total"] >= 2
        for item in search_data["items"]:
            assert "batch_user_1" in item["actor"]

        # Search filtered by severity="CRITICAL"
        res_search_sev = await client.get("/api/v1/events?severity=CRITICAL", headers=headers)
        assert res_search_sev.status_code == 200
        sev_data = res_search_sev.json()
        assert sev_data["total"] >= 1
        for item in sev_data["items"]:
            assert item["severity"] == "CRITICAL"


@pytest.mark.asyncio
async def test_unauthenticated_event_ingestion_blocked():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/events", json={"user": "attacker", "action": "probe"})
        assert res.status_code == 403 or res.status_code == 401
