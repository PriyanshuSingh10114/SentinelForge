import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database.init_db import init_db


@pytest.fixture(autouse=True)
async def prepare_db():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_owasp_a01_broken_access_control():
    """
    OWASP A01: Broken Access Control.
    Ensure non-admin users (e.g. Developer or Viewer) cannot access Admin or restricted APIs,
    returning strict 403 Forbidden without disclosing system internals.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as Developer
        dev_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "developer@sentinelforge.local", "password": "SentinelDev123!"},
        )
        assert dev_res.status_code == 200
        dev_token = dev_res.json()["access_token"]

        # 2. Attempt unauthorized policy creation (Admin only)
        forbidden_res = await client.post(
            "/api/v1/admin/policies",
            json={
                "name": "Malicious Policy Override",
                "description": "Attempted by dev",
                "policy_type": "DLP",
                "configuration": {"action": "ALLOW_ALL"},
            },
            headers={"Authorization": f"Bearer {dev_token}"},
        )
        assert forbidden_res.status_code == 403
        data = forbidden_res.json()
        assert data["error"]["code"] == "FORBIDDEN"
        assert "not authorized" in data["error"]["message"].lower() or "required" in data["error"]["message"].lower()

        # 3. Attempt unauthorized remediation approval (Admin only)
        remediation_res = await client.post(
            "/api/v1/remediations/fake-remediation-id/approve",
            json={"notes": "Bypassing approval"},
            headers={"Authorization": f"Bearer {dev_token}"},
        )
        assert remediation_res.status_code == 403


@pytest.mark.asyncio
async def test_owasp_a02_cryptographic_failures_and_secret_masking():
    """
    OWASP A02: Cryptographic Failures.
    Ensure passwords and credentials are never stored or returned in plaintext,
    and high-entropy tokens are masked by DLP before storage.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "analyst@sentinelforge.local", "password": "SentinelAnalyst123!"},
        )
        token = login_res.json()["access_token"]

        # Verify /auth/me never exposes password_hash
        me_res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert "password" not in me_data
        assert "password_hash" not in me_data

        # Ingest content containing raw sensitive secret
        raw_secret = "AKIA1111222233334444"
        dlp_res = await client.post(
            "/api/v1/dlp/scan",
            json={"content": f"Exported AWS_ACCESS_KEY_ID={raw_secret} to CI runner", "source_type": "PIPELINE"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert dlp_res.status_code == 200
        findings = dlp_res.json()["findings"]
        assert len(findings) > 0
        matched = findings[0]["matched_masked"]
        assert raw_secret not in matched
        assert "AKIA" in matched and "4444" in matched
        assert "*" in matched


@pytest.mark.asyncio
async def test_owasp_a03_injection_resilience():
    """
    OWASP A03: Injection.
    Verify parameterized event search handles SQL injection attempts cleanly without leaking errors.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "analyst@sentinelforge.local", "password": "SentinelAnalyst123!"},
        )
        token = login_res.json()["access_token"]

        # Classic SQLi payloads in query params
        sqli_payloads = [
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "\" UNION SELECT NULL, NULL, NULL --",
        ]
        for sqli in sqli_payloads:
            res = await client.get(
                f"/api/v1/events?actor={sqli}&event_type=login",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res.status_code == 200
            data = res.json()
            assert "items" in data
            assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_owasp_a07_identification_and_authentication_failures():
    """
    OWASP A07: Identification and Authentication Failures.
    Ensure progressive account throttling and lockout after repeated invalid authentication.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First 4 attempts return 401 Unauthorized
        for _ in range(4):
            res = await client.post(
                "/api/v1/auth/login",
                json={"email": "viewer@sentinelforge.local", "password": "WrongPasswordAttempt!"},
            )
            assert res.status_code == 401

        # 5th attempt reaches lockout threshold (MAX_FAILED_ATTEMPTS=5), triggers 403 Forbidden
        res_5 = await client.post(
            "/api/v1/auth/login",
            json={"email": "viewer@sentinelforge.local", "password": "WrongPasswordAttempt!"},
        )
        assert res_5.status_code == 403
        data_5 = res_5.json()
        assert "locked" in data_5["error"]["message"].lower()

        # Subsequent attempts are also blocked with 403
        res_subsequent = await client.post(
            "/api/v1/auth/login",
            json={"email": "viewer@sentinelforge.local", "password": "SentinelViewer123!"},
        )
        assert res_subsequent.status_code == 403


@pytest.mark.asyncio
async def test_owasp_a01_incident_and_threat_status_authorization():
    """
    OWASP A01: Broken Access Control.
    Ensure read-only Viewers cannot mutate incident life-cycle or suppress threats.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as Viewer
        viewer_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "viewer@sentinelforge.local", "password": "SentinelViewer123!"},
        )
        viewer_token = viewer_res.json()["access_token"]

        # Viewer attempts to resolve an incident -> 403 Forbidden
        inc_res = await client.patch(
            "/api/v1/incidents/nonexistent-id/status",
            json={"status": "RESOLVED"},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert inc_res.status_code == 403
        assert inc_res.json()["error"]["code"] == "FORBIDDEN"

        # Viewer attempts to mark threat item as FALSE_POSITIVE -> 403 Forbidden
        threat_res = await client.patch(
            "/api/v1/threat-models/items/nonexistent-id/status",
            json={"status": "FALSE_POSITIVE"},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert threat_res.status_code == 403
        assert threat_res.json()["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_scan_findings_and_ingest_rbac():
    """
    Verify RBAC on DevSecOps scan endpoints: Developers and Admins can ingest findings;
    all roles including Viewers can inspect scan findings.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as Developer
        dev_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "developer@sentinelforge.local", "password": "SentinelDev123!"},
        )
        dev_token = dev_res.json()["access_token"]

        # 2. Ingest a scan finding as Developer -> 201 Created
        scan_payload = {
            "scanner": "bandit",
            "rule_id": "B105",
            "severity": "HIGH",
            "file_path": "backend/app/core/config.py",
            "line_number": 26,
            "description": "Hardcoded demo key detected in dev config",
            "remediation": "Load from environment secrets",
        }
        ingest_res = await client.post(
            "/api/v1/scans/ingest",
            json=scan_payload,
            headers={"Authorization": f"Bearer {dev_token}"},
        )
        assert ingest_res.status_code == 201
        finding_id = ingest_res.json()["id"]

        # 3. Login as Viewer
        viewer_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "viewer@sentinelforge.local", "password": "SentinelViewer123!"},
        )
        viewer_token = viewer_res.json()["access_token"]

        # 4. Viewer cannot ingest scan findings -> 403 Forbidden
        viewer_ingest = await client.post(
            "/api/v1/scans/ingest",
            json=scan_payload,
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert viewer_ingest.status_code == 403

        # 5. Viewer CAN view scan findings -> 200 OK
        list_res = await client.get(
            "/api/v1/scans/findings",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert list_res.status_code == 200
        findings = list_res.json()
        assert any(f["id"] == finding_id for f in findings)


@pytest.mark.asyncio
async def test_admin_user_provisioning_and_policy_management():
    """
    Verify Admin-only provisioning of identities and full policy lifecycle.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as Admin
        admin_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@sentinelforge.local", "password": "SentinelAdmin123!"},
        )
        admin_token = admin_res.json()["access_token"]

        # 2. Provision new Analyst user -> 201 Created
        new_user_payload = {
            "email": "new.analyst@sentinelforge.local",
            "name": "New SOC Analyst",
            "password": "SecurePassword123!",
            "role_name": "Analyst",
        }
        create_res = await client.post(
            "/api/v1/admin/users",
            json=new_user_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_res.status_code == 201
        created_user = create_res.json()
        assert created_user["email"] == "new.analyst@sentinelforge.local"
        assert created_user["role"] == "Analyst"

        # 3. Duplicate email rejected -> 409 Conflict
        dup_res = await client.post(
            "/api/v1/admin/users",
            json=new_user_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert dup_res.status_code == 409

        # 4. List policies -> 200 OK
        policies_res = await client.get(
            "/api/v1/admin/policies",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert policies_res.status_code == 200
        policies = policies_res.json()
        assert len(policies) >= 1
        target_policy = policies[0]

        # 5. Update policy -> 200 OK
        update_res = await client.put(
            f"/api/v1/admin/policies/{target_policy['id']}",
            json={"enabled": not target_policy["enabled"]},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert update_res.status_code == 200
        assert update_res.json()["enabled"] != target_policy["enabled"]

        # 6. Non-admin is blocked from user provisioning -> 403 Forbidden
        analyst_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "analyst@sentinelforge.local", "password": "SentinelAnalyst123!"},
        )
        analyst_token = analyst_res.json()["access_token"]
        unauth_create = await client.post(
            "/api/v1/admin/users",
            json={"email": "hacker@test.local", "name": "Hacker", "password": "Password123!", "role_name": "Admin"},
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
        assert unauth_create.status_code == 403
