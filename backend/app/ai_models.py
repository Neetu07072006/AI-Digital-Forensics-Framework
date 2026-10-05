from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class AIInvestigation(Base):
    __tablename__ = "ai_investigations"

    investigation_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer,
        ForeignKey("cases.case_id"),
        nullable=False,
        index=True
    )
    summary = Column(Text, nullable=False)
    attack_pattern = Column(Text, nullable=True)
    risk_assessment = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    model = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())