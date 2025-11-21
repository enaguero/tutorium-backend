from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.session import SessionStatus
from app.schemas.user import User

if TYPE_CHECKING:
    from app.schemas.session_participant import ParticipantResponse


# Shared properties
class SessionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    max_participants: int = Field(default=50, ge=2, le=100)
    enable_recording: bool = False
    enable_chat: bool = True


# Properties to receive via API on creation
class SessionCreate(SessionBase):
    pass


# Properties to receive via API on update
class SessionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, ge=2, le=100)
    enable_recording: Optional[bool] = None
    enable_chat: Optional[bool] = None
    status: Optional[SessionStatus] = None


# Properties shared by models stored in DB
class SessionInDBBase(SessionBase):
    id: int
    teacher_id: int
    status: SessionStatus
    daily_room_name: str
    daily_room_url: str
    room_code: str
    actual_start: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Properties to return to client (basic info)
class SessionResponse(SessionInDBBase):
    teacher: User


# Properties to return to client (detailed info with participants)
class SessionDetailResponse(SessionResponse):
    participants: List["ParticipantResponse"] = []


# Properties for list responses
class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int
