from app.audit_models import AuditLog

def create_audit_log(
    db,
    username,
    action,
    resource=None,
    details=None
):
    log = AuditLog(
        username=username,
        action=action,
        resource=resource,
        details=details
    )

    db.add(log)
    db.commit()

    return log