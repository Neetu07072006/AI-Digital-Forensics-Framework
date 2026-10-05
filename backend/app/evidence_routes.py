import hashlib
import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.evidence_models import Evidence
from app.custody_models import ChainOfCustody
from app.security import require_roles

router = APIRouter(
    prefix="/api/evidence",
    tags=["Evidence"]
)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

MAX_FILE_SIZE = 100 * 1024 * 1024

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

@router.post("/upload")
def upload_evidence(
    case_id: int = Form(...),
    uploaded_by: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Investigator"
        )
    )
):
    case = db.query(Case).filter(
        Case.case_id == case_id
    ).first()

    if not case:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    original_name = os.path.basename(
        file.filename or ""
    )

    if not original_name:
        raise HTTPException(
            status_code=400,
            detail="Invalid file name"
        )

    extension = os.path.splitext(
        original_name
    )[1].lower()

    stored_name = (
        f"{uuid.uuid4().hex}{extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_name
    )

    file_size = 0
    sha256 = hashlib.sha256()

    try:
        with open(
            file_path,
            "wb"
        ) as buffer:
            while True:
                chunk = file.file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="Evidence file exceeds 100 MB limit"
                    )

                sha256.update(chunk)
                buffer.write(chunk)

    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail="Failed to store evidence file"
        )

    evidence = Evidence(
        case_id=case_id,
        file_name=original_name,
        file_path=file_path,
        file_size=file_size,
        file_type=file.content_type,
        sha256_hash=sha256.hexdigest(),
        description=description,
        uploaded_by=current_user.username
    )

    try:
        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        custody = ChainOfCustody(
            evidence_id=evidence.evidence_id,
            action="Evidence Uploaded",
            performed_by=current_user.username,
            details=(
                f"Original filename: {original_name}; "
                f"Stored filename: {stored_name}; "
                f"SHA-256: {evidence.sha256_hash}"
            )
        )

        db.add(custody)
        db.commit()

    except Exception:
        db.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail="Failed to save evidence metadata"
        )

    return {
        "message": "Evidence uploaded successfully",
        "evidence_id": evidence.evidence_id,
        "file_name": evidence.file_name,
        "stored_file_name": stored_name,
        "file_size": evidence.file_size,
        "sha256_hash": evidence.sha256_hash
    }

@router.get("/")
def get_evidence(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Investigator",
            "Analyst"
        )
    )
):
    evidence = db.query(Evidence).order_by(
        Evidence.created_at.desc()
    ).all()

    return [
        {
            "evidence_id": item.evidence_id,
            "case_id": item.case_id,
            "file_name": item.file_name,
            "file_size": item.file_size,
            "file_type": item.file_type,
            "sha256_hash": item.sha256_hash,
            "description": item.description,
            "uploaded_by": item.uploaded_by,
            "created_at": item.created_at
        }
        for item in evidence
    ]

@router.get("/{evidence_id}")
def get_evidence_details(
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

    return {
        "evidence_id": evidence.evidence_id,
        "case_id": evidence.case_id,
        "file_name": evidence.file_name,
        "file_path": evidence.file_path,
        "file_size": evidence.file_size,
        "file_type": evidence.file_type,
        "sha256_hash": evidence.sha256_hash,
        "description": evidence.description,
        "uploaded_by": evidence.uploaded_by,
        "created_at": evidence.created_at
    }

@router.post("/{evidence_id}/verify")
def verify_evidence(
    evidence_id: int,
    performed_by: str = Form(...),
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

    if not os.path.exists(evidence.file_path):
        raise HTTPException(
            status_code=404,
            detail="Evidence file not found"
        )

    sha256 = hashlib.sha256()

    with open(
        evidence.file_path,
        "rb"
    ) as evidence_file:
        for chunk in iter(
            lambda: evidence_file.read(
                1024 * 1024
            ),
            b""
        ):
            sha256.update(chunk)

    current_hash = sha256.hexdigest()

    integrity_verified = (
        current_hash == evidence.sha256_hash
    )

    action = (
        "Integrity Verified"
        if integrity_verified
        else "Tampering Detected"
    )

    custody = ChainOfCustody(
        evidence_id=evidence.evidence_id,
        action=action,
        performed_by=current_user.username,
        details=(
            f"Original SHA-256: {evidence.sha256_hash}; "
            f"Current SHA-256: {current_hash}"
        )
    )

    db.add(custody)
    db.commit()

    return {
        "evidence_id": evidence.evidence_id,
        "file_name": evidence.file_name,
        "original_hash": evidence.sha256_hash,
        "current_hash": current_hash,
        "integrity_verified": integrity_verified,
        "status": (
            "INTEGRITY VERIFIED"
            if integrity_verified
            else "TAMPERING DETECTED"
        )
    }

@router.get("/{evidence_id}/custody")
def get_chain_of_custody(
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

    records = db.query(
        ChainOfCustody
    ).filter(
        ChainOfCustody.evidence_id == evidence_id
    ).order_by(
        ChainOfCustody.timestamp.asc()
    ).all()

    return [
        {
            "custody_id": record.custody_id,
            "evidence_id": record.evidence_id,
            "action": record.action,
            "performed_by": record.performed_by,
            "details": record.details,
            "timestamp": record.timestamp
        }
        for record in records
    ]