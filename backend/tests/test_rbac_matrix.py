import pytest
from httpx import ASGITransport, AsyncClient
from app.database.init_db import init_db
from app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


async def get_token_for(client: AsyncClient, email: str, password: str) -> str:
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_all_four_profiles_rbac_matrix():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Obtain tokens for all 4 profiles
        admin_token = await get_token_for(client, "admin@sentinelforge.local", "SentinelAdmin123!")
        analyst_token = await get_token_for(client, "analyst@sentinelforge.local", "SentinelAnalyst123!")
        dev_token = await get_token_for(client, "developer@sentinelforge.local", "SentinelDev123!")
        viewer_token = await get_token_for(client, "viewer@sentinelforge.local", "SentinelViewer123!")

        # 2. Check /auth/me profile responses
        for token, expected_role in [
            (admin_token, "Admin"),
            (analyst_token, "Analyst"),
            (dev_token, "Developer"),
            (viewer_token, "Viewer"),
        ]:
            me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert me_res.status_code == 200
            assert me_res.json()["role"] == expected_role

        # 3. Test ADMIN ONLY: User Management
        # Admin -> 200
        res = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        # Analyst -> 403
        res = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {analyst_token}"})
        assert res.status_code == 403
        # Developer -> 403
        res = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {dev_token}"})
        assert res.status_code == 403
        # Viewer -> 403
        res = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {viewer_token}"})
        assert res.status_code == 403

        # 4. Test AUDIT LOGS: Admin and Analyst allowed, Dev and Viewer blocked
        res = await client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        res = await client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {analyst_token}"})
        assert res.status_code == 200
        res = await client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {dev_token}"})
        assert res.status_code == 403
        res = await client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {viewer_token}"})
        assert res.status_code == 403

        # 5. Test EVENT SIMULATION: Admin, Analyst, Dev allowed, Viewer blocked
        res_viewer_ev = await client.post("/api/v1/events/simulate", headers={"Authorization": f"Bearer {viewer_token}"})
        assert res_viewer_ev.status_code == 403

        res_dev_ev = await client.post("/api/v1/events/simulate", headers={"Authorization": f"Bearer {dev_token}"})
        assert res_dev_ev.status_code == 201

        # 6. Test THREAT MODEL CREATION: Admin, Analyst, Dev allowed, Viewer blocked
        arch_data = {"name": "Test Arch", "architecture_summary": "FastAPI gateway with PostgreSQL database and JWT tokens."}
        res_viewer_tm = await client.post("/api/v1/threat-models", json=arch_data, headers={"Authorization": f"Bearer {viewer_token}"})
        assert res_viewer_tm.status_code == 403

        res_dev_tm = await client.post("/api/v1/threat-models", json=arch_data, headers={"Authorization": f"Bearer {dev_token}"})
        assert res_dev_tm.status_code == 201

        # 7. Test DEVSECOPS SCAN INGESTION: Admin and Developer allowed, Analyst and Viewer blocked
        scan_data = {
            "scanner": "bandit",
            "rule_id": "B105",
            "severity": "HIGH",
            "file_path": "test.py",
            "description": "Hardcoded test credential",
            "remediation": "Remove secret",
        }
        res_analyst_scan = await client.post("/api/v1/scans/ingest", json=scan_data, headers={"Authorization": f"Bearer {analyst_token}"})
        assert res_analyst_scan.status_code == 403

        res_viewer_scan = await client.post("/api/v1/scans/ingest", json=scan_data, headers={"Authorization": f"Bearer {viewer_token}"})
        assert res_viewer_scan.status_code == 403

        res_dev_scan = await client.post("/api/v1/scans/ingest", json=scan_data, headers={"Authorization": f"Bearer {dev_token}"})
        assert res_dev_scan.status_code == 201

