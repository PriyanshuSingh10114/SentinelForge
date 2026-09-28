import pytest
from httpx import ASGITransport, AsyncClient
from app.database.init_db import init_db
from app.main import app


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()
    from sqlalchemy import update
    from app.database.session import AsyncSessionLocal
    from app.models.auth import User
    async with AsyncSessionLocal() as session:
        await session.execute(update(User).values(failed_login_attempts=0, locked_until=None))
        await session.commit()


@pytest.mark.asyncio
async def test_successful_login_and_token_generation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login with demo admin
        res = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@sentinelforge.local", "password": "SentinelAdmin123!"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

        token = data["access_token"]

        # 2. Inspect /auth/me
        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == "admin@sentinelforge.local"
        assert me_data["role"] == "Admin"
        assert "policy:write" in me_data["permissions"]


@pytest.mark.asyncio
async def test_failed_login_and_progressive_lockout():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 4 failed attempts
        for _ in range(4):
            res = await client.post(
                "/api/v1/auth/login",
                json={"email": "developer@sentinelforge.local", "password": "WrongPassword!"},
            )
            assert res.status_code == 401
            assert res.json()["error"]["code"] == "UNAUTHORIZED"

        # 5th failed attempt -> locks account
        res5 = await client.post(
            "/api/v1/auth/login",
            json={"email": "developer@sentinelforge.local", "password": "WrongPassword!"},
        )
        assert res5.status_code == 403
        assert res5.json()["error"]["code"] == "FORBIDDEN"
        assert "Account locked" in res5.json()["error"]["message"]

        # Even with correct password, locked account is blocked
        res_locked = await client.post(
            "/api/v1/auth/login",
            json={"email": "developer@sentinelforge.local", "password": "SentinelDev123!"},
        )
        assert res_locked.status_code == 403
        assert "Account is locked" in res_locked.json()["error"]["message"]


@pytest.mark.asyncio
async def test_server_side_rbac_developer_blocked_from_admin():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as Developer (use Analyst password for fresh login without lockout)
        res_dev = await client.post(
            "/api/v1/auth/login",
            json={"email": "analyst@sentinelforge.local", "password": "SentinelAnalyst123!"},
        )
        analyst_token = res_dev.json()["access_token"]

        # Analyst attempts to create policy (Admin only)
        res_blocked = await client.post(
            "/api/v1/admin/policies",
            json={
                "name": "Unauthorized Policy",
                "description": "Analyst should not be able to create policies",
                "policy_type": "DLP",
                "configuration": {},
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
        assert res_blocked.status_code == 403
        err = res_blocked.json()["error"]
        assert err["code"] == "FORBIDDEN"
        assert "not authorized for this operation" in err["message"]

        # Analyst attempts to list all users (Admin only)
        res_users_blocked = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
        assert res_users_blocked.status_code == 403


@pytest.mark.asyncio
async def test_admin_authorized_operations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as Admin
        res_admin = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@sentinelforge.local", "password": "SentinelAdmin123!"},
        )
        admin_token = res_admin.json()["access_token"]

        # 1. Admin creates policy
        import uuid
        pol_name = f"Quarantine High Entropy Tokens {uuid.uuid4().hex[:6]}"
        res_pol = await client.post(
            "/api/v1/admin/policies",
            json={
                "name": pol_name,
                "description": "Quarantine API tokens with high Shannon entropy",
                "policy_type": "DLP",
                "configuration": {"entropy_threshold": 4.5},
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_pol.status_code == 201
        data = res_pol.json()
        assert data["name"] == pol_name

        # 2. Admin lists users
        res_users = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_users.status_code == 200
        users = res_users.json()
        assert len(users) >= 4


@pytest.mark.asyncio
async def test_token_refresh_and_logout_revocation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as Viewer
        res = await client.post(
            "/api/v1/auth/login",
            json={"email": "viewer@sentinelforge.local", "password": "SentinelViewer123!"},
        )
        tokens = res.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Refresh token
        ref_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert ref_res.status_code == 200
        new_tokens = ref_res.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != access_token

        # Logout with new access token
        logout_res = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        assert logout_res.status_code == 200

        # Try to use revoked access token -> 401
        revoked_call = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
        )
        assert revoked_call.status_code == 401
        assert "Token has been revoked" in revoked_call.json()["error"]["message"]
