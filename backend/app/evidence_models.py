from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from app.database import Base

class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.case_id"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    file_type = Column(String(100), nullable=True)
    sha256_hash = Column(String(64), nullable=False, index=True)
    description = Column(Text, nullable=True)
    uploaded_by = Column(String(150), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())