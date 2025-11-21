from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.models.session_participant import ParticipantRole, ConnectionStatus
from app.schemas.user import User


# Properties to return to client
class ParticipantResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    role: ParticipantRole
    connection_status: ConnectionStatus
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    created_at: datetime
    user: User
    
    class Config:
        from_attributes = True
