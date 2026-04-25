from flask_jwt_extended import get_jwt


def get_claim_roles() -> set[str]:
    claims = get_jwt()
    return set(claims.get("roles", []))


def get_claim_org_ids() -> set[int]:
    claims = get_jwt()
    return {int(org_id) for org_id in claims.get("organization_ids", []) if org_id is not None}


def is_platform_scope() -> bool:
    roles = get_claim_roles()
    return "government_admin" in roles or "platform_admin" in roles
