import pytest
from sqlalchemy import select
from app.database.init_db import init_db, DEMO_USERS
from app.database.session import AsyncSessionLocal
from app.models import (
    User,
    Role,
    Permission,
    DataClassification,
    Asset,
    SecurityPolicy,
    SecurityEvent,
    Incident,
)
from app.security.password import verify_password


@pytest.mark.asyncio
async def test_database_initialization_and_seeding():
    # 1. Run database initialization
    await init_db()

    async with AsyncSessionLocal() as session:
        # 2. Verify Roles
        roles_res = await session.execute(select(Role))
        roles = roles_res.scalars().all()
        role_names = {r.name for r in roles}
        assert {"Admin", "Analyst", "Developer", "Viewer"}.issubset(role_names)

        # 3. Verify Admin has all permissions
        admin_role = next(r for r in roles if r.name == "Admin")
        admin_perms = {p.name for p in admin_role.permissions}
        assert "user:manage" in admin_perms
        assert "policy:write" in admin_perms
        assert "remediation:approve" in admin_perms

        # 4. Verify Developer has restricted permissions
        dev_role = next(r for r in roles if r.name == "Developer")
        dev_perms = {p.name for p in dev_role.permissions}
        assert "scan:submit" in dev_perms
        assert "policy:write" not in dev_perms
        assert "remediation:approve" not in dev_perms

        # 5. Verify Data Classifications
        classif_res = await session.execute(select(DataClassification))
        classifs = classif_res.scalars().all()
        c_names = {c.name for c in classifs}
        assert {"PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"} == c_names

        # 6. Verify Demo Users & Bcrypt Password Hashing
        for demo in DEMO_USERS:
            stmt = select(User).where(User.email == demo["email"])
            res = await session.execute(stmt)
            user = res.scalar_one_or_none()
            assert user is not None
            assert user.is_active is True
            # Password must NOT be plaintext
            assert user.password_hash != demo["password"]
            assert user.password_hash.startswith("$2b$") or user.password_hash.startswith("$2a$")
            # Verification must succeed
            assert verify_password(demo["password"], user.password_hash) is True
            # Invalid password must fail
            assert verify_password("WrongPassword!", user.password_hash) is False

        # 7. Verify Assets and Policies
        assets_res = await session.execute(select(Asset))
        assets = assets_res.scalars().all()
        assert len(assets) >= 4

        policies_res = await session.execute(select(SecurityPolicy))
        policies = policies_res.scalars().all()
        assert len(policies) >= 2


@pytest.mark.asyncio
async def test_security_event_and_incident_relationship():
    from datetime import datetime, timezone

    import uuid
    inc_num = f"INC-TEST-{uuid.uuid4().hex[:6].upper()}"

    async with AsyncSessionLocal() as session:
        # Create an event
        event = SecurityEvent(
            event_type="test_probe",
            severity="HIGH",
            source="unit_test",
            actor="test_subject",
            source_ip="192.168.1.100",
            timestamp=datetime.now(timezone.utc),
            raw_payload={"action": "test_access"},
            normalized_payload={"actor": "test_subject", "ip": "192.168.1.100"},
        )
        session.add(event)
        await session.flush()

        # Create an incident linked to the event
        incident = Incident(
            incident_number=inc_num,
            title="Unit Test Correlation Incident",
            description="Testing foreign keys and many-to-many relationship",
            severity="HIGH",
            status="OPEN",
            risk_score=75,
            confidence=0.950,
            events=[event],
        )
        session.add(incident)
        await session.commit()

        # Query incident and verify correlated events
        stmt = select(Incident).where(Incident.incident_number == inc_num)
        res = await session.execute(stmt)
        saved_inc = res.scalar_one_or_none()
        assert saved_inc is not None
        assert len(saved_inc.events) == 1
        assert saved_inc.events[0].event_type == "test_probe"
