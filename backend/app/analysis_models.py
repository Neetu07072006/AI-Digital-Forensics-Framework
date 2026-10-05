from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class AnalysisFinding(Base):
    __tablename__ = "analysis_findings"

    finding_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer,
        ForeignKey("cases.case_id"),
        nullable=False,
        index=True
    )
    evidence_id = Column(
        Integer,
        ForeignKey("evidence.evidence_id"),
        nullable=False,
        index=True
    )
    artifact_id = Column(
        Integer,
        ForeignKey("artifacts.artifact_id"),
        nullable=True,
        index=True
    )
    finding_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    risk_score = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence_reference = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())