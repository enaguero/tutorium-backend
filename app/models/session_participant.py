from sqlalchemy import Column, Integer, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class ParticipantRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"


class ConnectionStatus(str, enum.Enum):
    INVITED = "invited"
    JOINED = "joined"
    LEFT = "left"
    KICKED = "kicked"


class SessionParticipant(Base):
    __tablename__ = "session_participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(ParticipantRole), nullable=False)
    connection_status = Column(SQLEnum(ConnectionStatus), default=ConnectionStatus.INVITED)
    
    # Timing
    joined_at = Column(DateTime, nullable=True)
    left_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("Session", back_populates="participants")
    user = relationship("User", back_populates="session_participations")
