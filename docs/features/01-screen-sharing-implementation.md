# Screen Sharing Feature - FastAPI Backend Implementation Guide

This document provides detailed step-by-step implementation instructions for the backend component of the screen sharing feature. Refer to [`01-screen-sharing.md`](01-screen-sharing.md) for the feature specification.

## Prerequisites

- FastAPI backend already set up (✅ confirmed)
- PostgreSQL database configured
- SQLAlchemy ORM and Alembic for migrations
- Existing user authentication with JWT
- `httpx` library available (confirmed in requirements.txt)

---

## Step 1: Environment Configuration

### 1.1 Update Configuration Settings

**File**: `app/core/config.py`

Add Daily.co configuration to the existing `Settings` class:

```python
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tutorium API"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/tutorium"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Daily.co Integration (NEW)
    DAILY_API_KEY: str = ""
    DAILY_DOMAIN: str = "tutorium.daily.co"
    DAILY_WEBHOOK_SECRET: str = ""
    DAILY_API_BASE_URL: str = "https://api.daily.co/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### 1.2 Update .env.example

Add these lines to `.env.example`:

```bash
# Daily.co Integration
DAILY_API_KEY=your_daily_api_key_here
DAILY_DOMAIN=your-domain.daily.co
DAILY_WEBHOOK_SECRET=your_webhook_secret_here
```

### 1.3 Update Your .env File

Copy the above and add your actual credentials after signing up at https://www.daily.co/

---

## Step 2: Database Models

### 2.1 Create Session Model

**File**: `app/models/session.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class SessionStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.SCHEDULED, nullable=False)
    
    # Daily.co integration fields
    daily_room_name = Column(String(100), unique=True, nullable=False, index=True)
    daily_room_url = Column(String(255), nullable=False)
    room_code = Column(String(20), unique=True, nullable=False, index=True)
    
    # Timing
    scheduled_start = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Settings
    max_participants = Column(Integer, default=50)
    enable_recording = Column(Boolean, default=False)
    enable_chat = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = relationship("User", back_populates="sessions")
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    events = relationship("SessionEvent", back_populates="session", cascade="all, delete-orphan")
```

### 2.2 Create SessionParticipant Model

**File**: `app/models/session_participant.py`

```python
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
```

### 2.3 Create SessionEvent Model

**File**: `app/models/session_event.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class SessionEvent(Base):
    __tablename__ = "session_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="events")
    user = relationship("User")
```

### 2.4 Update User Model

**File**: `app/models/user.py`

Add relationships to the existing `User` class:

```python
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # NEW: Add relationships
    sessions = relationship("Session", back_populates="teacher")
    session_participations = relationship("SessionParticipant", back_populates="user")
```

### 2.5 Update Model Imports

**File**: `app/models/__init__.py`

```python
from app.models.user import User
from app.models.session import Session, SessionStatus
from app.models.session_participant import SessionParticipant, ParticipantRole, ConnectionStatus
from app.models.session_event import SessionEvent
```

### 2.6 Register Models with Alembic

**File**: `app/db/base.py`

Ensure all models are imported so Alembic can detect them:

```python
from app.db.session import Base

# Import all models here for Alembic
from app.models.user import User
from app.models.session import Session
from app.models.session_participant import SessionParticipant
from app.models.session_event import SessionEvent
```

---

## Step 3: Pydantic Schemas

### 3.1 Session Schemas

**File**: `app/schemas/session.py`

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.session import SessionStatus


class SessionBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    max_participants: int = Field(default=50, ge=1, le=100)
    enable_recording: bool = False
    enable_chat: bool = True


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[SessionStatus] = None
    scheduled_start: Optional[datetime] = None


class SessionResponse(SessionBase):
    id: int
    teacher_id: int
    status: SessionStatus
    daily_room_url: str
    room_code: str
    actual_start: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SessionDetailResponse(SessionResponse):
    teacher_join_url: str
    participant_count: int = 0


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int
```

### 3.2 Participant Schemas

**File**: `app/schemas/session_participant.py`

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.session_participant import ParticipantRole, ConnectionStatus


class ParticipantResponse(BaseModel):
    id: int
    session_id: int
    user_id: int
    role: ParticipantRole
    connection_status: ConnectionStatus
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### 3.3 Join Session Schemas

**File**: `app/schemas/session_join.py`

```python
from pydantic import BaseModel


class JoinSessionResponse(BaseModel):
    join_url: str
    room_name: str
    token: str


class JoinByCodeRequest(BaseModel):
    room_code: str


class JoinByCodeResponse(BaseModel):
    session_id: int
    join_url: str
    room_name: str
    token: str
```

### 3.4 Update Schema Imports

**File**: `app/schemas/__init__.py`

```python
from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.session import (
    SessionCreate, SessionUpdate, SessionResponse, 
    SessionDetailResponse, SessionListResponse
)
from app.schemas.session_participant import ParticipantResponse
from app.schemas.session_join import JoinSessionResponse, JoinByCodeRequest, JoinByCodeResponse
```

---

## Step 4: Daily.co Service

### 4.1 Create Daily.co API Client

**File**: `app/services/daily_client.py`

```python
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings


class DailyAPIError(Exception):
    """Exception raised for Daily.co API errors"""
    pass


class DailyClient:
    """Client for Daily.co REST API"""
    
    def __init__(self):
        self.base_url = settings.DAILY_API_BASE_URL
        self.api_key = settings.DAILY_API_KEY
        self.domain = settings.DAILY_DOMAIN
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_room(
        self,
        room_name: str,
        max_participants: int = 50,
        enable_recording: bool = False,
        enable_chat: bool = True,
        exp_hours: int = 4
    ) -> Dict[str, Any]:
        """Create a Daily.co room"""
        exp_timestamp = int((datetime.utcnow() + timedelta(hours=exp_hours)).timestamp())
        
        payload = {
            "name": room_name,
            "privacy": "private",
            "properties": {
                "max_participants": max_participants,
                "enable_screenshare": True,
                "enable_chat": enable_chat,
                "enable_recording": "cloud" if enable_recording else "off",
                "start_video_off": True,
                "start_audio_off": False,
                "exp": exp_timestamp
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rooms",
                json=payload,
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code not in [200, 201]:
                raise DailyAPIError(f"Failed to create room: {response.text}")
            
            return response.json()
    
    async def create_meeting_token(
        self,
        room_name: str,
        user_name: str,
        user_id: str,
        is_owner: bool = False,
        enable_screenshare: bool = False,
        exp_hours: int = 4
    ) -> str:
        """Create a meeting token for a participant"""
        exp_timestamp = int((datetime.utcnow() + timedelta(hours=exp_hours)).timestamp())
        
        payload = {
            "properties": {
                "room_name": room_name,
                "user_name": user_name,
                "user_id": user_id,
                "is_owner": is_owner,
                "enable_screenshare": enable_screenshare,
                "exp": exp_timestamp
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/meeting-tokens",
                json=payload,
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code not in [200, 201]:
                raise DailyAPIError(f"Failed to create token: {response.text}")
            
            return response.json()["token"]
    
    async def delete_room(self, room_name: str) -> bool:
        """Delete a Daily.co room"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/rooms/{room_name}",
                headers=self.headers,
                timeout=10.0
            )
            
            if response.status_code not in [200, 204]:
                raise DailyAPIError(f"Failed to delete room: {response.text}")
            
            return True


# Singleton instance
daily_client = DailyClient()
```

### 4.2 Create Services Directory

```bash
mkdir -p app/services
touch app/services/__init__.py
```

---

## Step 5: CRUD Operations

### 5.1 Create Session CRUD

**File**: `app/crud/session.py`

```python
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import secrets
import string

from app.models.session import Session as SessionModel, SessionStatus
from app.models.session_participant import SessionParticipant, ParticipantRole, ConnectionStatus
from app.schemas.session import SessionCreate, SessionUpdate


def generate_room_code(length: int = 6) -> str:
    """Generate a random room code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))


def create_session(
    db: Session,
    session_in: SessionCreate,
    teacher_id: int,
    daily_room_name: str,
    daily_room_url: str
) -> SessionModel:
    """Create a new session"""
    room_code = generate_room_code()
    
    # Ensure room code is unique
    while db.query(SessionModel).filter(SessionModel.room_code == room_code).first():
        room_code = generate_room_code()
    
    db_session = SessionModel(
        teacher_id=teacher_id,
        title=session_in.title,
        description=session_in.description,
        scheduled_start=session_in.scheduled_start,
        max_participants=session_in.max_participants,
        enable_recording=session_in.enable_recording,
        enable_chat=session_in.enable_chat,
        daily_room_name=daily_room_name,
        daily_room_url=daily_room_url,
        room_code=room_code,
        status=SessionStatus.SCHEDULED
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Add teacher as participant
    teacher_participant = SessionParticipant(
        session_id=db_session.id,
        user_id=teacher_id,
        role=ParticipantRole.TEACHER,
        connection_status=ConnectionStatus.INVITED
    )
    db.add(teacher_participant)
    db.commit()
    
    return db_session


def get_session(db: Session, session_id: int) -> Optional[SessionModel]:
    """Get session by ID"""
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()


def get_session_by_room_code(db: Session, room_code: str) -> Optional[SessionModel]:
    """Get session by room code"""
    return db.query(SessionModel).filter(SessionModel.room_code == room_code).first()


def get_sessions_by_teacher(
    db: Session,
    teacher_id: int,
    status: Optional[SessionStatus] = None,
    skip: int = 0,
    limit: int = 100
) -> List[SessionModel]:
    """Get sessions for a teacher"""
    query = db.query(SessionModel).filter(SessionModel.teacher_id == teacher_id)
    
    if status:
        query = query.filter(SessionModel.status == status)
    
    return query.offset(skip).limit(limit).all()


def get_sessions_by_student(
    db: Session,
    student_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[SessionModel]:
    """Get sessions where user is a participant"""
    return (
        db.query(SessionModel)
        .join(SessionParticipant)
        .filter(
            and_(
                SessionParticipant.user_id == student_id,
                SessionParticipant.role == ParticipantRole.STUDENT
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_session(
    db: Session,
    session_id: int,
    session_update: SessionUpdate
) -> Optional[SessionModel]:
    """Update a session"""
    db_session = get_session(db, session_id)
    if not db_session:
        return None
    
    update_data = session_update.model_dump(exclude_unset=True)
    
    # Handle status transitions
    if "status" in update_data:
        if update_data["status"] == SessionStatus.ACTIVE and not db_session.actual_start:
            update_data["actual_start"] = datetime.utcnow()
        elif update_data["status"] == SessionStatus.ENDED and not db_session.ended_at:
            update_data["ended_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: int) -> bool:
    """Delete a session"""
    db_session = get_session(db, session_id)
    if not db_session:
        return False
    
    db.delete(db_session)
    db.commit()
    return True


def add_participant(
    db: Session,
    session_id: int,
    user_id: int,
    role: ParticipantRole = ParticipantRole.STUDENT
) -> SessionParticipant:
    """Add a participant to session"""
    # Check if already participant
    existing = (
        db.query(SessionParticipant)
        .filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id
            )
        )
        .first()
    )
    
    if existing:
        return existing
    
    participant = SessionParticipant(
        session_id=session_id,
        user_id=user_id,
        role=role,
        connection_status=ConnectionStatus.INVITED
    )
    
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def update_participant_status(
    db: Session,
    session_id: int,
    user_id: int,
    status: ConnectionStatus
) -> Optional[SessionParticipant]:
    """Update participant connection status"""
    participant = (
        db.query(SessionParticipant)
        .filter(
            and_(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id
            )
        )
        .first()
    )
    
    if not participant:
        return None
    
    participant.connection_status = status
    
    if status == ConnectionStatus.JOINED and not participant.joined_at:
        participant.joined_at = datetime.utcnow()
    elif status == ConnectionStatus.LEFT and not participant.left_at:
        participant.left_at = datetime.utcnow()
    
    db.commit()
    db.refresh(participant)
    return participant


def get_session_participants(db: Session, session_id: int) -> List[SessionParticipant]:
    """Get all participants for a session"""
    return (
        db.query(SessionParticipant)
        .filter(SessionParticipant.session_id == session_id)
        .all()
    )
```

### 5.2 Create CRUD Module Directory

```bash
# If not exists
mkdir -p app/crud
```

Update `app/crud/__init__.py`:

```python
from app.crud import user, session
```

---

## Step 6: API Endpoints

### 6.1 Create Session Endpoints

**File**: `app/api/v1/endpoints/sessions.py`

Due to length, see the full implementation in the main implementation plan document. Key endpoints:

- `POST /api/v1/sessions` - Create session
- `GET /api/v1/sessions/{id}` - Get session
- `GET /api/v1/sessions` - List sessions
- `PATCH /api/v1/sessions/{id}` - Update session
- `DELETE /api/v1/sessions/{id}` - Delete session
- `POST /api/v1/sessions/{id}/join` - Join session
- `POST /api/v1/sessions/{id}/leave` - Leave session
- `POST /api/v1/sessions/join-by-code` - Join by code
- `GET /api/v1/sessions/{id}/participants` - List participants

### 6.2 Register Routes

**File**: `app/api/v1/router.py`

```python
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, sessions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
```

---

## Step 7: Database Migration

```bash
# Create migration
alembic revision --autogenerate -m "add session, session_participant, and session_event tables"

# Review the generated migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

---

## Step 8: Testing

### 8.1 Start the Server

```bash
uvicorn app.main:app --reload
```

### 8.2 Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 8.3 Test Flow

1. Login to get JWT token
2. Create a session (POST /api/v1/sessions)
3. Get session details (GET /api/v1/sessions/{id})
4. Join session (POST /api/v1/sessions/{id}/join)
5. Test with Daily.co room URL

---

## Next Steps

1. Implement webhook endpoint (Week 2)
2. Add event logging
3. Write unit and integration tests
4. Deploy to staging environment

---

## Troubleshooting

### Issue: Daily.co API returns 401
- Check `DAILY_API_KEY` is correct in .env
- Verify API key is active in Daily.co dashboard

### Issue: Migration fails
- Check all models are imported in `app/db/base.py`
- Verify database connection string
- Run `alembic revision` manually if autogenerate fails

### Issue: Token validation fails
- Check JWT configuration in `app/core/security.py`
- Verify `SECRET_KEY` is set correctly

---

**Implementation Status**: Ready to begin  
**Estimated Time**: Week 1 of Phase 2 (11-12 hours)
