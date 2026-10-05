from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    event_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer,
        ForeignKey("cases.case_id"),
        nullable=False,
        index=True
    )
    evidence_id = Column(
        Integer,
        ForeignKey("evidence.evidence_id"),
        nullable=True,
        index=True
    )
    event_type = Column(String(100), nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    severity = Column(String(50), default="Informational")
    created_at = Column(DateTime(timezone=True), server_default=func.now())