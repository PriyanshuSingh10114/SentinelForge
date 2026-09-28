import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from app.database.init_db import init_db
from app.database.session import AsyncSessionLocal
from app.dlp.classifier import classify_text_content
from app.main import app
from app.models.dlp import DlpFinding


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


async def get_analyst_token(client: AsyncClient) -> str:
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@sentinelforge.local", "password": "SentinelAnalyst123!"},
    )
    return res.json()["access_token"]


def test_shannon_entropy_detection():
    # Low entropy natural English
    normal_text = "This is a regular message describing platform deployment configurations."
    findings_normal = classify_text_content(normal_text)
    assert len(findings_normal) == 0

    # High entropy simulated base64 key
    high_entropy_token = "4kL9z!pQ#7wM2vX$8bN1rT%5yH0cE3jU"
    findings_entropy = classify_text_content(f"API_SECRET={high_entropy_token}")
    entropy_matches = [f for f in findings_entropy if f.data_type == "HIGH_ENTROPY_SECRET"]
    assert len(entropy_matches) >= 1
    assert entropy_matches[0].classification == "RESTRICTED"
    assert high_entropy_token not in entropy_matches[0].matched_masked


@pytest.mark.asyncio
async def test_dlp_scan_aws_key_block_and_masking():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_analyst_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        raw_aws_key = "AKIAIOSFODNN7EXAMPLE"
        content = f"AWS_ACCESS_KEY_ID={raw_aws_key}\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

        res = await client.post(
            "/api/v1/dlp/scan",
            json={"content": content, "source_type": "FILE_UPLOAD", "source_id": ".env"},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["classification"] == "RESTRICTED"
        assert data["action"] == "BLOCK"
        assert data["findings_count"] >= 1

        aws_finding = next(f for f in data["findings"] if f["data_type"] == "AWS_ACCESS_KEY")
        assert aws_finding["classification"] == "RESTRICTED"
        assert aws_finding["matched_masked"].startswith("AKIA")
        assert aws_finding["matched_masked"].endswith("MPLE")
        assert "*" in aws_finding["matched_masked"]

        # ZERO PLAINTEXT GUARANTEE: Raw secret must NEVER be stored in the database
        async with AsyncSessionLocal() as session:
            stmt = select(DlpFinding).where(DlpFinding.source_id == ".env")
            db_res = await session.execute(stmt)
            saved_findings = db_res.scalars().all()
            assert len(saved_findings) >= 1
            for sf in saved_findings:
                assert raw_aws_key not in sf.matched_pattern
                assert sf.action == "BLOCK"


@pytest.mark.asyncio
async def test_dlp_scan_pii_warn_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_analyst_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        content = "Customer inquiry from John Doe: contact john.doe@example.org or (555) 234-5678"
        res = await client.post(
            "/api/v1/dlp/scan",
            json={"content": content, "source_type": "PAYLOAD"},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["classification"] == "CONFIDENTIAL"
        assert data["action"] == "WARN"
        assert any(f["data_type"] == "EMAIL_PII" for f in data["findings"])
        assert any(f["data_type"] == "PHONE_NUMBER" for f in data["findings"])


@pytest.mark.asyncio
async def test_dlp_scan_database_uri_masking():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_analyst_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        db_uri = "postgresql://prod_admin:SuperSecretPass123!@10.0.1.50:5432/core_db"
        res = await client.post(
            "/api/v1/dlp/scan",
            json={"content": f"DATABASE_URL={db_uri}", "source_type": "CONFIG"},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["classification"] == "RESTRICTED"
        assert data["action"] == "BLOCK"

        db_finding = next(f for f in data["findings"] if f["data_type"] == "DATABASE_URI")
        assert "SuperSecretPass123!" not in db_finding["matched_masked"]
        assert "prod_admin" in db_finding["matched_masked"]
        assert "****************" in db_finding["matched_masked"]
