from typing import Any, Dict, List


SECURITY_KNOWLEDGE_DOCS = [
    {
        "id": "KB-OWASP-01",
        "title": "OWASP A01:2021 - Broken Access Control",
        "category": "OWASP",
        "min_role": "Viewer",
        "content": (
            "Broken Access Control occurs when users can act outside of their intended permissions. "
            "Mitigations: Deny access by default, enforce server-side record ownership checks, and disable directory listings."
        ),
    },
    {
        "id": "KB-OWASP-02",
        "title": "OWASP A02:2021 - Cryptographic Failures",
        "category": "OWASP",
        "min_role": "Viewer",
        "content": (
            "Cryptographic failures expose sensitive data in transit or at rest. "
            "Mitigations: Never store secrets or passwords in plaintext; mask tokens upon ingestion; enforce TLS 1.3."
        ),
    },
    {
        "id": "KB-OWASP-03",
        "title": "OWASP A03:2021 - Injection",
        "category": "OWASP",
        "min_role": "Developer",
        "content": (
            "Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. "
            "Mitigations: Use parameterized queries in SQLAlchemy; validate inputs with Pydantic schemas."
        ),
    },
    {
        "id": "KB-POLICY-01",
        "title": "Internal Incident Response Procedure - High Severity Incidents",
        "category": "INTERNAL_POLICY",
        "min_role": "Analyst",
        "content": (
            "Procedure for HIGH and CRITICAL incidents: Immediately contain compromised accounts via session revocation. "
            "Isolate affected compute resources. Document the attack chain with verified event logs. High-impact remediation requires Admin approval."
        ),
    },
    {
        "id": "KB-POLICY-02",
        "title": "Restricted Master Key Rotation & Disaster Recovery",
        "category": "ADMIN_POLICY",
        "min_role": "Admin",  # Admin only!
        "content": (
            "Admin-only secret rotation procedure: Upon compromise of AWS root or master STS credentials, "
            "immediately revoke IAM access keys via AWS Console or CLI, rotate KMS customer master keys, and audit CloudTrail."
        ),
    },
]

ROLE_RANKS = {"Viewer": 1, "Developer": 2, "Analyst": 3, "Admin": 4}


def search_knowledge_base(query: str, user_role: str = "Analyst", limit: int = 3) -> List[Dict[str, str]]:
    """
    Retrieves security knowledge base articles enforcing strict role-based access filtering.
    A Developer or Viewer cannot retrieve Admin-only procedures.
    """
    user_rank = ROLE_RANKS.get(user_role, 1)
    query_terms = [t.lower() for t in query.split() if len(t) > 2]

    scored = []
    for doc in SECURITY_KNOWLEDGE_DOCS:
        # 1. Enforce RBAC filtering
        doc_rank = ROLE_RANKS.get(doc["min_role"], 4)
        if user_rank < doc_rank:
            continue  # Authorization gate: exclude document

        # 2. Relevance scoring
        score = 0
        doc_text = f"{doc['title']} {doc['content']} {doc['category']}".lower()
        for term in query_terms:
            if term in doc_text:
                score += 1

        if score > 0 or not query_terms:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"id": d["id"], "title": d["title"], "category": d["category"], "content": d["content"]}
        for _, d in scored[:limit]
    ]
