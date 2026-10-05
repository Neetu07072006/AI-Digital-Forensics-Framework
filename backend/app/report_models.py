from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class ForensicReport(Base):
    __tablename__ = "forensic_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer,
        ForeignKey("cases.case_id"),
        nullable=False,
        index=True
    )
    report_title = Column(String(255), nullable=False)
    report_path = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    risk_level = Column(String(50), nullable=True)
    risk_score = Column(Integer, nullable=True)
    generated_by = Column(String(150), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())