from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic
from app.models.user import User
from app.models.session import Session
from app.models.session_participant import SessionParticipant
from app.models.session_event import SessionEvent
