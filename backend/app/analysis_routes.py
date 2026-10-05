from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.evidence_models import Evidence
from app.artifact_models import Artifact
from app.analysis_models import AnalysisFinding
from app.analysis_engine import analyze_artifacts, calculate_case_risk
from app.security import require_roles

router = APIRouter(
    prefix="/api/analysis",
    tags=["AI Analysis"]
)

@router.post("/{case_id}/analyze")
def analyze_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Investigator",
            "Analyst"
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

    db.query(AnalysisFinding).filter(
        AnalysisFinding.case_id == case_id
    ).delete()

    evidence_items = db.query(Evidence).filter(
        Evidence.case_id == case_id
    ).all()

    all_findings = []

    for evidence in evidence_items:
        artifacts = db.query(Artifact).filter(
            Artifact.evidence_id == evidence.evidence_id
        ).all()

        findings = analyze_artifacts(artifacts)

        for finding in findings:
            database_finding = AnalysisFinding(
                case_id=case_id,
                evidence_id=evidence.evidence_id,
                artifact_id=finding["artifact_id"],
                finding_type=finding["finding_type"],
                severity=finding["severity"],
                risk_score=finding["risk_score"],
                title=finding["title"],
                description=finding["description"],
                evidence_reference=finding["evidence_reference"]
            )

            db.add(database_finding)
            all_findings.append(finding)

    db.commit()

    risk = calculate_case_risk(all_findings)

    return {
        "case_id": case_id,
        "findings_detected": len(all_findings),
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "message": "Forensic threat analysis completed"
    }

@router.get("/{case_id}")
def get_case_analysis(
    case_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Investigator",
            "Analyst"
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

    findings = db.query(AnalysisFinding).filter(
        AnalysisFinding.case_id == case_id
    ).order_by(
        AnalysisFinding.risk_score.desc(),
        AnalysisFinding.created_at.asc()
    ).all()

    risk = calculate_case_risk([
        {
            "risk_score": finding.risk_score
        }
        for finding in findings
    ])

    return {
        "case_id": case_id,
        "risk_score": risk["risk_score"],
        "risk_level": risk["risk_level"],
        "findings": [
            {
                "finding_id": finding.finding_id,
                "evidence_id": finding.evidence_id,
                "artifact_id": finding.artifact_id,
                "finding_type": finding.finding_type,
                "severity": finding.severity,
                "risk_score": finding.risk_score,
                "title": finding.title,
                "description": finding.description,
                "evidence_reference": finding.evidence_reference,
                "created_at": finding.created_at
            }
            for finding in findings
        ]
    }