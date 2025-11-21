# This file imports all models so Alembic can detect them
# Import Base first, then all models
from app.db.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.session import Session  # noqa: F401
from app.models.session_participant import SessionParticipant  # noqa: F401
from app.models.session_event import SessionEvent  # noqa: F401
