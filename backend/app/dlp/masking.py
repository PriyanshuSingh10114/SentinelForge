def mask_secret(secret: str, prefix_len: int = 4, suffix_len: int = 4) -> str:
    """
    Masks sensitive secrets and credentials to ensure they are never persisted or displayed in plaintext.
    Example: 'AKIAIOSFODNN7EXAMPLE' -> 'AKIA****************MPLE'
    """
    if not secret:
        return ""
    clean = secret.strip()
    if len(clean) <= (prefix_len + suffix_len):
        # Short secret: mask entirely
        return "*" * len(clean)

    prefix = clean[:prefix_len]
    suffix = clean[-suffix_len:]
    asterisks = "*" * max(16, len(clean) - (prefix_len + suffix_len))
    return f"{prefix}{asterisks}{suffix}"


def mask_connection_string(uri: str) -> str:
    """
    Masks credentials in database URIs:
    'postgres://dbadmin:SuperSecret123@prod-db:5432/main' -> 'postgres://dbadmin:****@prod-db:5432/main'
    """
    import re
    return re.sub(r"://([^:]+):([^@]+)@", r"://\1:****************@", uri)
