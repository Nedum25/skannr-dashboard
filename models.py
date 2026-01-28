# models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class TriageLog(Base):
    __tablename__ = "triage_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # user input
    symptoms_text = Column(Text, nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String, nullable=True)
    pregnancy = Column(Boolean, nullable=True)
    implants = Column(Text, nullable=True)      # store as comma-separated string
    location = Column(String, nullable=True)

    # AI / engine output
    triage = Column(String, nullable=False)      # e.g. URGENT_EMERGENCY / NON_EMERGENCY
    recommendation = Column(String, nullable=True)
    primary_modality = Column(String, nullable=True)
    primary_priority = Column(String, nullable=True)
    model_name = Column(String, nullable=True)   # e.g. "gemini-2.0-flash-001"

    notes = Column(Text, nullable=True)

    # one-to-one feedback (optional)
    feedback = relationship("ClinicianFeedback", back_populates="log", uselist=False)


class ClinicianFeedback(Base):
    __tablename__ = "clinician_feedback"

    id = Column(Integer, primary_key=True, index=True)
    triage_log_id = Column(Integer, ForeignKey("triage_logs.id"), unique=True)
    clinician_scan = Column(String, nullable=True)       # final scan chosen by clinician
    accepted_recommendation = Column(Boolean, nullable=True)
    comment = Column(Text, nullable=True)

    log = relationship("TriageLog", back_populates="feedback")
