from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_routes import get_current_user
from app.security import require_roles
from app.audit_models import AuditLog

router = APIRouter(
    prefix="/api/audit",
    tags=["Audit"]
)

@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("Admin")
    )
):
    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).all()

    return [
        {
            "audit_id": log.audit_id,
            "username": log.username,
            "action": log.action,
            "resource": log.resource,
            "details": log.details,
            "timestamp": log.timestamp
        }
        for log in logs
    ]