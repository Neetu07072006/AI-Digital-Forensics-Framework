from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CaseCreate(BaseModel):
    case_name: str
    description: str | None = None
    investigator: str
    status: str = "Open"
    priority: str = "Medium"

class CaseResponse(CaseCreate):
    case_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)