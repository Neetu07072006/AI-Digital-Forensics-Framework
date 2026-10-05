from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class ChainOfCustody(Base):
    __tablename__ = "chain_of_custody"

    custody_id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(
        Integer,
        ForeignKey("evidence.evidence_id"),
        nullable=False,
        index=True
    )
    action = Column(String(100), nullable=False)
    performed_by = Column(String(150), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())