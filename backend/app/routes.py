from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.schemas import CaseCreate, CaseResponse
from app.security import require_roles

router = APIRouter(
    prefix="/api/cases",
    tags=["Cases"]
)

@router.post(
    "/",
    response_model=CaseResponse
)
def create_case(
    case: CaseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles("Admin", "Investigator")
    )
):
    new_case = Case(
        case_name=case.case_name,
        description=case.description,
        investigator=case.investigator,
        status=case.status,
        priority=case.priority
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    return new_case

@router.get(
    "/",
    response_model=list[CaseResponse]
)
def get_cases(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Admin",
            "Investigator",
            "Analyst"
        )
    )
):
    return db.query(Case).order_by(
        Case.created_at.desc()
    ).all()

@router.get(
    "/{case_id}",
    response_model=CaseResponse
)
def get_case(
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

    return case