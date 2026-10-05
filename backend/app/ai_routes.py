from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.evidence_models import Evidence
from app.analysis_models import AnalysisFinding
from app.timeline_models import TimelineEvent
from app.ai_models import AIInvestigation
from app.ai_engine import (
    build_investigation_context,
    generate_ai_investigation
)
from app.security import require_roles

router = APIRouter(
    prefix="/api/ai",
    tags=["AI Investigation"]
)

@router.post("/{case_id}/investigate")
def investigate_case(
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

    evidence = db.query(Evidence).filter(
        Evidence.case_id == case_id
    ).all()

    findings = db.query(AnalysisFinding).filter(
        AnalysisFinding.case_id == case_id
    ).order_by(
        AnalysisFinding.risk_score.desc()
    ).all()

    timeline = db.query(TimelineEvent).filter(
        TimelineEvent.case_id == case_id
    ).order_by(
        TimelineEvent.event_time.asc()
    ).all()

    context = build_investigation_context(
        case,
        evidence,
        findings,
        timeline
    )

    result = generate_ai_investigation(context)

    investigation = AIInvestigation(
        case_id=case_id,
        summary=result["summary"],
        attack_pattern=result["attack_pattern"],
        risk_assessment=result["risk_assessment"],
        recommendations=result["recommendations"],
        model=result["model"]
    )

    db.add(investigation)
    db.commit()
    db.refresh(investigation)

    return {
        "investigation_id": investigation.investigation_id,
        "case_id": case_id,
        "summary": investigation.summary,
        "attack_pattern": investigation.attack_pattern,
        "risk_assessment": investigation.risk_assessment,
        "recommendations": investigation.recommendations,
        "model": investigation.model,
        "created_at": investigation.created_at
    }

@router.get("/{case_id}")
def get_ai_investigations(
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

    investigations = db.query(
        AIInvestigation
    ).filter(
        AIInvestigation.case_id == case_id
    ).order_by(
        AIInvestigation.created_at.desc()
    ).all()

    return [
        {
            "investigation_id": item.investigation_id,
            "case_id": item.case_id,
            "summary": item.summary,
            "attack_pattern": item.attack_pattern,
            "risk_assessment": item.risk_assessment,
            "recommendations": item.recommendations,
            "model": item.model,
            "created_at": item.created_at
        }
        for item in investigations
    ]