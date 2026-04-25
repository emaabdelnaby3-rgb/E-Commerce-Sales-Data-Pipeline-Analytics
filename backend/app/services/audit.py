from app.extensions import db
from app.models import AuditLog


def write_audit_log(actor_user_id, action: str, entity_type: str, entity_id: str, details: dict | None = None):
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=details or {},
    )
    db.session.add(entry)
