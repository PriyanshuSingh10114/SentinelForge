from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.database.session import Base, engine, AsyncSessionLocal
from app.models import (
    Role,
    Permission,
    RolePermission,
    User,
    DataClassification,
    Asset,
    SecurityPolicy,
)
from app.security.password import hash_password


DEFAULT_PERMISSIONS = [
    ("user:manage", "Full user and identity access management"),
    ("role:manage", "Role and permissions configuration"),
    ("policy:read", "Read security and DLP policies"),
    ("policy:write", "Create and modify security policies"),
    ("incident:read", "View security incidents and timelines"),
    ("incident:investigate", "Execute AI and manual investigations"),
    ("remediation:request", "Submit remediation recommendations"),
    ("remediation:approve", "Approve and execute high-risk remediation actions"),
    ("scan:submit", "Submit application artifacts for security scan"),
    ("scan:read", "View security scan reports"),
    ("audit:read", "Inspect immutable security audit logs"),
]

ROLE_PERMISSION_MAP = {
    "Admin": [p[0] for p in DEFAULT_PERMISSIONS],  # Full permissions
    "Analyst": [
        "incident:read",
        "incident:investigate",
        "remediation:request",
        "scan:read",
        "policy:read",
        "audit:read",
    ],
    "Developer": [
        "scan:submit",
        "scan:read",
        "incident:read",  # Own assigned/related findings
    ],
    "Viewer": [
        "incident:read",
        "scan:read",
        "policy:read",
    ],
}

DEMO_USERS = [
    {
        "email": "admin@sentinelforge.local",
        "name": "SecOps Administrator",
        "role": "Admin",
        "password": "SentinelAdmin123!",
    },
    {
        "email": "analyst@sentinelforge.local",
        "name": "Cyber Defense Analyst",
        "role": "Analyst",
        "password": "SentinelAnalyst123!",
    },
    {
        "email": "developer@sentinelforge.local",
        "name": "Lead Application Developer",
        "role": "Developer",
        "password": "SentinelDev123!",
    },
    {
        "email": "viewer@sentinelforge.local",
        "name": "Executive Observer",
        "role": "Viewer",
        "password": "SentinelViewer123!",
    },
]

DATA_CLASSIFICATIONS = [
    ("PUBLIC", "Public information freely shareable externally", 0),
    ("INTERNAL", "Internal business data not intended for public disclosure", 10),
    ("CONFIDENTIAL", "Sensitive customer records, PII, and financial transactions", 20),
    ("RESTRICTED", "High-risk credentials, master keys, tokens, and core database connection strings", 35),
]


async def init_db() -> None:
    """
    Creates database tables and seeds initial baseline data (roles, permissions, classifications, demo users).
    """
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Permissions
        perm_map = {}
        for name, desc in DEFAULT_PERMISSIONS:
            stmt = select(Permission).where(Permission.name == name)
            res = await session.execute(stmt)
            perm = res.scalar_one_or_none()
            if not perm:
                perm = Permission(name=name, description=desc)
                session.add(perm)
                await session.flush()
            perm_map[name] = perm

        # 2. Seed Roles & RolePermissions
        role_map = {}
        for role_name, allowed_perms in ROLE_PERMISSION_MAP.items():
            stmt = select(Role).where(Role.name == role_name)
            res = await session.execute(stmt)
            role = res.scalar_one_or_none()
            if not role:
                role = Role(name=role_name, description=f"Default {role_name} security role")
                session.add(role)
                await session.flush()
            role_map[role_name] = role

            # Associate permissions
            for p_name in allowed_perms:
                p_obj = perm_map.get(p_name)
                if p_obj:
                    rp_stmt = select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == p_obj.id,
                    )
                    rp_res = await session.execute(rp_stmt)
                    if not rp_res.scalar_one_or_none():
                        session.add(RolePermission(role_id=role.id, permission_id=p_obj.id))

        # 3. Seed Classifications
        classif_map = {}
        for c_name, c_desc, c_weight in DATA_CLASSIFICATIONS:
            stmt = select(DataClassification).where(DataClassification.name == c_name)
            res = await session.execute(stmt)
            classif = res.scalar_one_or_none()
            if not classif:
                classif = DataClassification(name=c_name, description=c_desc, severity_weight=c_weight)
                session.add(classif)
                await session.flush()
            classif_map[c_name] = classif

        # 4. Seed Default Assets
        default_assets = [
            ("customer-portal-api", "API", "production", "Platform Team", classif_map.get("RESTRICTED")),
            ("auth-service-cluster", "SERVER", "production", "SecOps", classif_map.get("RESTRICTED")),
            ("s3-customer-documents", "BUCKET", "production", "Data Engineering", classif_map.get("CONFIDENTIAL")),
            ("dev-internal-repo", "REPOSITORY", "development", "DevSecOps", classif_map.get("INTERNAL")),
        ]
        for a_name, a_type, a_env, a_owner, a_classif in default_assets:
            stmt = select(Asset).where(Asset.name == a_name)
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                asset = Asset(
                    name=a_name,
                    type=a_type,
                    environment=a_env,
                    owner=a_owner,
                    classification_id=a_classif.id if a_classif else None,
                    asset_metadata={"criticality": "HIGH" if a_env == "production" else "LOW"},
                )
                session.add(asset)

        # 5. Seed Demo Users
        for u in DEMO_USERS:
            stmt = select(User).where(User.email == u["email"])
            res = await session.execute(stmt)
            existing_user = res.scalar_one_or_none()
            if not existing_user:
                role_obj = role_map[u["role"]]
                user = User(
                    email=u["email"],
                    name=u["name"],
                    password_hash=hash_password(u["password"]),
                    role_id=role_obj.id,
                    is_active=True,
                )
                session.add(user)

        # 6. Seed Baseline DLP & Rate Limit Policies
        baseline_policies = [
            (
                "Block Cloud Credentials in Ingestion",
                "Immediately quarantine and block any incoming payload containing unmasked AWS or Cloud secrets",
                "DLP",
                {"action": "BLOCK", "target_types": ["AWS_ACCESS_KEY", "PRIVATE_KEY"]},
            ),
            (
                "Warn on PII Detection",
                "Flag email and phone number occurrences in API payloads as confidential",
                "DLP",
                {"action": "WARN", "target_types": ["EMAIL_PII", "PHONE_NUMBER"]},
            ),
        ]
        for p_name, p_desc, p_type, p_conf in baseline_policies:
            stmt = select(SecurityPolicy).where(SecurityPolicy.name == p_name)
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                session.add(
                    SecurityPolicy(
                        name=p_name,
                        description=p_desc,
                        policy_type=p_type,
                        configuration=p_conf,
                        enabled=True,
                    )
                )

        await session.commit()
    logger.info("Database schema and seed data initialized successfully.")
