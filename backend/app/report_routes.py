import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.evidence_models import Evidence
from app.analysis_models import AnalysisFinding
from app.timeline_models import TimelineEvent
from app.ai_models import AIInvestigation
from app.report_models import ForensicReport
from app.report_engine import generate_forensic_report
from app.security import require_roles

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)

@router.post("/{case_id}/generate")
def generate_report(
    case_id: int,
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

    ai_investigation = db.query(
        AIInvestigation
    ).filter(
        AIInvestigation.case_id == case_id
    ).order_by(
        AIInvestigation.created_at.desc()
    ).first()

    risk_score = min(
        sum(
            finding.risk_score
            for finding in findings
        ),
        100
    )

    if risk_score >= 80:
        risk_level = "Critical"
    elif risk_score >= 60:
        risk_level = "High"
    elif risk_score >= 30:
        risk_level = "Medium"
    elif risk_score > 0:
        risk_level = "Low"
    else:
        risk_level = "Informational"

    report_path = generate_forensic_report(
        case,
        evidence,
        findings,
        timeline,
        ai_investigation
    )

    report = ForensicReport(
        case_id=case_id,
        report_title=f"Forensic Report - {case.case_name}",
        report_path=report_path,
        summary=(
            ai_investigation.summary
            if ai_investigation
            else case.description
        ),
        risk_level=risk_level,
        risk_score=risk_score,
        generated_by=current_user.username
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.report_id,
        "case_id": case_id,
        "report_title": report.report_title,
        "report_path": report.report_path,
        "risk_score": report.risk_score,
        "risk_level": report.risk_level,
        "generated_by": report.generated_by,
        "message": "Forensic report generated successfully"
    }

@router.get("/{case_id}")
def get_case_reports(
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

    reports = db.query(
        ForensicReport
    ).filter(
        ForensicReport.case_id == case_id
    ).order_by(
        ForensicReport.created_at.desc()
    ).all()

    return [
        {
            "report_id": report.report_id,
            "case_id": report.case_id,
            "report_title": report.report_title,
            "report_path": report.report_path,
            "summary": report.summary,
            "risk_level": report.risk_level,
            "risk_score": report.risk_score,
            "generated_by": report.generated_by,
            "created_at": report.created_at
        }
        for report in reports
    ]

@router.get("/{case_id}/download")
def download_latest_report(
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

    report = db.query(
        ForensicReport
    ).filter(
        ForensicReport.case_id == case_id
    ).order_by(
        ForensicReport.created_at.desc()
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="No report found for this case"
        )

    if not report.report_path:
        raise HTTPException(
            status_code=404,
            detail="Report path not available"
        )

    if not os.path.exists(report.report_path):
        raise HTTPException(
            status_code=404,
            detail="Report file not found"
        )

    return FileResponse(
        report.report_path,
        media_type="application/pdf",
        filename=f"case_{case_id}_forensic_report.pdf"
    )