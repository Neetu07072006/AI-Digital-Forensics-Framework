from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.evidence_models import Evidence
from app.custody_models import ChainOfCustody
from app.timeline_models import TimelineEvent
from app.timeline_engine import extract_file_timeline
from app.security import require_roles

router = APIRouter(
    prefix="/api/timeline",
    tags=["Timeline"]
)

@router.post("/{case_id}/generate")
def generate_timeline(
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

    db.query(TimelineEvent).filter(
        TimelineEvent.case_id == case_id
    ).delete()

    evidence_items = db.query(Evidence).filter(
        Evidence.case_id == case_id
    ).all()

    event_count = 0

    for evidence in evidence_items:
        try:
            events = extract_file_timeline(
                evidence.file_path
            )
        except FileNotFoundError:
            continue

        for event in events:
            timeline_event = TimelineEvent(
                case_id=case_id,
                evidence_id=evidence.evidence_id,
                event_type=event["event_type"],
                event_time=event["event_time"],
                title=event["title"],
                description=event["description"],
                source=event["source"],
                severity=event["severity"]
            )

            db.add(timeline_event)
            event_count += 1

    custody_records = db.query(
        ChainOfCustody
    ).join(
        Evidence,
        ChainOfCustody.evidence_id == Evidence.evidence_id
    ).filter(
        Evidence.case_id == case_id
    ).all()

    for record in custody_records:
        timeline_event = TimelineEvent(
            case_id=case_id,
            evidence_id=record.evidence_id,
            event_type="CHAIN_OF_CUSTODY",
            event_time=record.timestamp,
            title=record.action,
            description=record.details,
            source="Chain of Custody",
            severity="Informational"
        )

        db.add(timeline_event)
        event_count += 1

    db.commit()

    return {
        "case_id": case_id,
        "events_generated": event_count,
        "message": "Timeline generated successfully"
    }

@router.get("/{case_id}")
def get_timeline(
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

    events = db.query(TimelineEvent).filter(
        TimelineEvent.case_id == case_id
    ).order_by(
        TimelineEvent.event_time.asc()
    ).all()

    return [
        {
            "event_id": event.event_id,
            "case_id": event.case_id,
            "evidence_id": event.evidence_id,
            "event_type": event.event_type,
            "event_time": event.event_time,
            "title": event.title,
            "description": event.description,
            "source": event.source,
            "severity": event.severity
        }
        for event in events
    ]