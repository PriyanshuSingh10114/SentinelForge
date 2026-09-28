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
async def test_stride_threat_model_creation_and_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_analyst_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        arch_summary = (
            "React Web Frontend communicates with FastAPI Gateway using JWT tokens. "
            "Backend performs parameterized queries on PostgreSQL database cluster, "
            "stores confidential documents in AWS S3 buckets, and streams immutable audit records to CloudWatch."
        )

        # 1. Create Threat Model
        res = await client.post(
            "/api/v1/threat-models",
            json={"name": "SentinelForge Core Architecture", "architecture_summary": arch_summary},
            headers=headers,
        )
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "SentinelForge Core Architecture"
        assert len(data["items"]) >= 5

        # Verify STRIDE coverage
        categories = {item["stride_category"] for item in data["items"]}
        assert "SPOOFING" in categories
        assert "TAMPERING" in categories
        assert "INFO_DISCLOSURE" in categories
        assert "DOS" in categories
        assert "ELEVATION" in categories
        assert "REPUDIATION" in categories

        model_id = data["id"]
        first_item_id = data["items"][0]["id"]
        second_item_id = data["items"][1]["id"]

        # 2. Get Threat Model Detail
        detail_res = await client.get(f"/api/v1/threat-models/{model_id}", headers=headers)
        assert detail_res.status_code == 200
        assert len(detail_res.json()["items"]) == len(data["items"])

        # 3. Update Status to MITIGATED
        patch_res = await client.patch(
            f"/api/v1/threat-models/items/{first_item_id}/status",
            json={"status": "MITIGATED"},
            headers=headers,
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["status"] == "MITIGATED"

        # 4. Update Status to ACCEPTED
        patch_res2 = await client.patch(
            f"/api/v1/threat-models/items/{second_item_id}/status",
            json={"status": "ACCEPTED"},
            headers=headers,
        )
        assert patch_res2.status_code == 200
        assert patch_res2.json()["status"] == "ACCEPTED"
