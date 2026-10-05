from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.evidence_models import Evidence
from app.artifact_models import Artifact
from app.artifact_engine import extract_artifacts
from app.security import require_roles

router = APIRouter(
    prefix="/api/artifacts",
    tags=["Artifacts"]
)

@router.post("/{evidence_id}/extract")
def extract_evidence_artifacts(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Investigator",
            "Analyst"
        )
    )
):
    evidence = db.query(Evidence).filter(
        Evidence.evidence_id == evidence_id
    ).first()

    if not evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found"
        )

    try:
        results = extract_artifacts(
            evidence.file_path
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Evidence file not found"
        )

    db.query(Artifact).filter(
        Artifact.evidence_id == evidence_id
    ).delete()

    artifacts = []

    for value in results["urls"]:
        artifacts.append(
            Artifact(
                evidence_id=evidence_id,
                artifact_type="URL",
                artifact_value=value,
                source=evidence.file_name
            )
        )

    for value in results["ips"]:
        artifacts.append(
            Artifact(
                evidence_id=evidence_id,
                artifact_type="IP",
                artifact_value=value,
                source=evidence.file_name
            )
        )

    for value in results["emails"]:
        artifacts.append(
            Artifact(
                evidence_id=evidence_id,
                artifact_type="EMAIL",
                artifact_value=value,
                source=evidence.file_name
            )
        )

    for value in results["suspicious_keywords"]:
        artifacts.append(
            Artifact(
                evidence_id=evidence_id,
                artifact_type="SUSPICIOUS_KEYWORD",
                artifact_value=value,
                source=evidence.file_name
            )
        )

    for value in results["strings"][:100]:
        artifacts.append(
            Artifact(
                evidence_id=evidence_id,
                artifact_type="STRING",
                artifact_value=value,
                source=evidence.file_name
            )
        )

    db.add_all(artifacts)
    db.commit()

    return {
        "evidence_id": evidence_id,
        "file_name": results["file_name"],
        "file_size": results["file_size"],
        "md5": results["md5"],
        "sha256": results["sha256"],
        "urls_found": len(results["urls"]),
        "ips_found": len(results["ips"]),
        "emails_found": len(results["emails"]),
        "suspicious_keywords_found": len(
            results["suspicious_keywords"]
        ),
        "strings_found": len(results["strings"]),
        "message": "Artifact extraction completed"
    }

@router.get("/{evidence_id}")
def get_artifacts(
    evidence_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Investigator",
            "Analyst"
        )
    )
):
    evidence = db.query(Evidence).filter(
        Evidence.evidence_id == evidence_id
    ).first()

    if not evidence:
        raise HTTPException(
            status_code=404,
            detail="Evidence not found"
        )

    artifacts = db.query(Artifact).filter(
        Artifact.evidence_id == evidence_id
    ).order_by(
        Artifact.created_at.asc()
    ).all()

    return [
        {
            "artifact_id": artifact.artifact_id,
            "evidence_id": artifact.evidence_id,
            "artifact_type": artifact.artifact_type,
            "artifact_value": artifact.artifact_value,
            "source": artifact.source,
            "created_at": artifact.created_at
        }
        for artifact in artifacts
    ]