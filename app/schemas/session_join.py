from pydantic import BaseModel, Field


# Request to join session by room code
class JoinByCodeRequest(BaseModel):
    room_code: str = Field(..., min_length=1, max_length=20)


# Response when successfully joining a session
class JoinSessionResponse(BaseModel):
    session_id: int
    daily_room_url: str
    meeting_token: str
    room_code: str
    message: str = "Successfully joined session"
