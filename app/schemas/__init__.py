from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.session import (
    SessionBase,
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionDetailResponse,
    SessionListResponse,
)
from app.schemas.session_participant import ParticipantResponse
from app.schemas.session_join import JoinByCodeRequest, JoinSessionResponse

# Rebuild models with forward references
SessionDetailResponse.model_rebuild()
