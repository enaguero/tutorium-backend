# Phase 2: Screen Sharing with Daily.co - Implementation Plan

## 📈 Progress Tracker

**Week 1: Core Backend Implementation**
- ✅ Step 1: Environment Setup (30 min) - COMPLETED
- ✅ Step 2: Database Models (2 hours) - COMPLETED  
- ⏳ Step 3: Pydantic Schemas (1.5 hours) - IN PROGRESS
- ⏳ Step 4: Daily.co Service (2 hours) - PENDING
- ⏳ Step 5: CRUD Operations (2 hours) - PENDING
- ⏳ Step 6: API Endpoints (3 hours) - PENDING
- ⏳ Step 7: Database Migration (30 min) - PENDING
- ⏳ Step 8: Manual Testing (1 hour) - PENDING

**Overall Progress**: 2/8 steps completed (25%)

**PRs Created**:
- PR #2: Daily.co Setup & Configuration
- PR #3: Database Models

---

## Current State Analysis
**Backend Status**:
- ✅ FastAPI backend with JWT authentication
- ✅ SQLAlchemy ORM with PostgreSQL
- ✅ User model and basic auth endpoints exist
- ✅ `httpx` library available for API calls
- ❌ No Daily.co integration yet
- ❌ No session-related models or endpoints
- ❌ Router endpoints commented out (needs investigation)

**Daily.co Integration Model**:
- Uses REST API for server-side operations (room creation, token generation)
- Frontend uses `@daily-co/daily-js` SDK to join rooms and handle WebRTC
- Token-based security with role-based permissions (owner vs participant)
- Meeting tokens are JWTs signed by Daily.co

## System Architecture & Flow Diagrams

### High-Level Architecture
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Teacher   │         │   Student    │         │   Student   │
│  (Frontend) │         │  (Frontend)  │         │  (Frontend) │
└──────┬──────┘         └──────┬───────┘         └──────┬──────┘
       │                       │                        │
       │ HTTPS (JWT Auth)      │                        │
       │                       │                        │
       ▼                       ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Tutorium FastAPI Backend                       │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Session Management & Daily.co Integration       │      │
│  │  - Create rooms via Daily.co API                 │      │
│  │  - Generate meeting tokens (owner/participant)   │      │
│  │  - Track session state in PostgreSQL             │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ HTTPS (API Key Auth)
              │
              ▼
    ┌───────────────────┐
    │   Daily.co API    │
    │  - Room Management│
    │  - Token Generation│
    │  - Webhooks       │
    └─────────┬─────────┘
              │
              │ WebRTC Media Streams
              │
    ┌─────────▼──────────┐
    │  Daily.co WebRTC   │
    │  Infrastructure    │
    │  (SFU Mesh)        │
    └────────────────────┘
              ▲
              │ WebRTC connections
         ┌────┴────┬────────────┐
         │         │            │
   Teacher's   Student's    Student's
   Browser     Browser      Browser
```

### Teacher Session Creation Flow
```
Teacher Frontend                Backend API                 Daily.co API          Database
      │                            │                            │                    │
      │  1. POST /sessions         │                            │                    │
      │  {title, description}      │                            │                    │
      ├───────────────────────────>│                            │                    │
      │                            │                            │                    │
      │                            │  2. POST /v1/rooms         │                    │
      │                            │  {name, privacy:private,   │                    │
      │                            │   enable_screenshare:true} │                    │
      │                            ├───────────────────────────>│                    │
      │                            │                            │                    │
      │                            │  3. Room Data              │                    │
      │                            │  {url, name}               │                    │
      │                            │<───────────────────────────┤                    │
      │                            │                            │                    │
      │                            │  4. Save Session           │                    │
      │                            │  (room_url, room_code,     │                    │
      │                            │   status:scheduled)        │                    │
      │                            ├───────────────────────────────────────────────>│
      │                            │                            │                    │
      │                            │  5. POST /v1/meeting-tokens│                    │
      │                            │  {room_name, is_owner:true,│                    │
      │                            │   enable_screenshare:true} │                    │
      │                            ├───────────────────────────>│                    │
      │                            │                            │                    │
      │                            │  6. Owner Token            │                    │
      │                            │<───────────────────────────┤                    │
      │                            │                            │                    │
      │  7. Session Created        │                            │                    │
      │  {id, room_code,           │                            │                    │
      │   teacher_join_url}        │                            │                    │
      │<───────────────────────────┤                            │                    │
      │                            │                            │                    │
```

### Teacher Joins & Starts Screen Sharing
```
Teacher Frontend          Backend API          Daily.co API      Daily.co WebRTC
      │                      │                      │                  │
      │  1. POST /sessions/{id}/join                │                  │
      │  (JWT in header)     │                      │                  │
      ├─────────────────────>│                      │                  │
      │                      │                      │                  │
      │                      │  2. Generate token   │                  │
      │                      │  (is_owner:true)     │                  │
      │                      ├─────────────────────>│                  │
      │                      │                      │                  │
      │                      │  3. Meeting Token    │                  │
      │                      │<─────────────────────┤                  │
      │                      │                      │                  │
      │                      │  4. Update status    │                  │
      │                      │  (JOINED)            │                  │
      │                      │                      │                  │
      │  5. Join URL + Token │                      │                  │
      │<─────────────────────┤                      │                  │
      │                      │                      │                  │
      │  6. daily.join({url, token})                │                  │
      ├─────────────────────────────────────────────────────────────>│
      │                      │                      │                  │
      │  7. WebRTC negotiation (STUN/TURN/ICE)      │                  │
      │<────────────────────────────────────────────────────────────>│
      │                      │                      │                  │
      │  8. daily.startScreenShare()                │                  │
      ├─────────────────────────────────────────────────────────────>│
      │                      │                      │                  │
      │  9. Screen stream published to SFU          │                  │
      │                      │                      │                  │
```

### Student Joins & Views Screen Share
```
Student Frontend          Backend API          Daily.co API      Daily.co WebRTC
      │                      │                      │                  │
      │  1. POST /sessions/join-by-code             │                  │
      │  {room_code: "ABC123"}                      │                  │
      ├─────────────────────>│                      │                  │
      │                      │                      │                  │
      │                      │  2. Lookup session   │                  │
      │                      │  by room_code        │                  │
      │                      │                      │                  │
      │                      │  3. Generate token   │                  │
      │                      │  (is_owner:false,    │                  │
      │                      │   enable_screenshare:false)            │
      │                      ├─────────────────────>│                  │
      │                      │                      │                  │
      │                      │  4. Meeting Token    │                  │
      │                      │<─────────────────────┤                  │
      │                      │                      │                  │
      │                      │  5. Add participant  │                  │
      │                      │  (role:STUDENT)      │                  │
      │                      │                      │                  │
      │  6. Join URL + Token │                      │                  │
      │<─────────────────────┤                      │                  │
      │                      │                      │                  │
      │  7. daily.join({url, token})                │                  │
      ├─────────────────────────────────────────────────────────────>│
      │                      │                      │                  │
      │  8. WebRTC negotiation                      │                  │
      │<────────────────────────────────────────────────────────────>│
      │                      │                      │                  │
      │  9. Receive teacher's screen stream         │                  │
      │<────────────────────────────────────────────────────────────>│
      │                      │                      │                  │
      │  10. Display screen share                   │                  │
      │  (automatic via Daily Prebuilt)             │                  │
      │                      │                      │                  │
```

### Frontend-Backend Interaction Summary
**Backend Responsibilities**:
1. Session CRUD (create, read, update, delete)
2. User authentication & authorization
3. Daily.co room creation via REST API
4. Meeting token generation with role-based permissions
5. Session state tracking (scheduled, active, ended)
6. Participant management
7. Webhook processing (optional for Phase 1)

**Frontend Responsibilities**:
1. UI for session creation/joining
2. Display session details (room code, participants)
3. Embed Daily.co using `@daily-co/daily-js`
4. Handle Daily.co events (participant joined/left, screen share started/stopped)
5. Control screen sharing (teacher only)
6. Display media streams

**Daily.co Responsibilities**:
1. WebRTC infrastructure (STUN/TURN servers)
2. Media routing (SFU)
3. Screen capture and streaming
4. Built-in UI (Daily Prebuilt)
5. Connection quality management

## Implementation Steps

### Week 1: Core Backend Implementation

**Step 1: Environment Setup** ✅ (30 min) - COMPLETED
- ✅ Add Daily.co config to `app/core/config.py`
- ✅ Update `.env.example` with Daily.co vars
- ⏳ Get Daily.co API key from dashboard (user action required)
- 📝 PR #2: https://github.com/enaguero/tutorium-backend/pull/2
- 📄 Setup guide created: `docs/DAILY_SETUP.md`

**Step 2: Database Models** ✅ (2 hours) - COMPLETED
- ✅ Create `app/models/session.py` (Session, SessionStatus enum)
- ✅ Create `app/models/session_participant.py` (SessionParticipant, ParticipantRole, ConnectionStatus)
- ✅ Create `app/models/session_event.py` (SessionEvent)
- ✅ Update `app/models/user.py` with relationships
- ✅ Update `app/models/__init__.py`
- ✅ Update `app/db/base.py` for Alembic detection
- 📝 PR #3: https://github.com/enaguero/tutorium-backend/pull/3
- ✨ Field sizes optimized: daily_room_name (255), daily_room_url (512)

**Step 3: Pydantic Schemas** (1.5 hours)
- Create `app/schemas/session.py`
- Create `app/schemas/session_participant.py`
- Create `app/schemas/session_join.py`
- Update `app/schemas/__init__.py`

**Step 4: Daily.co Service** (2 hours)
- Create `app/services/` directory
- Create `app/services/daily_client.py` with:
  - `DailyClient` class
  - `create_room()` method
  - `create_meeting_token()` method
  - `delete_room()` method
  - Error handling with `DailyAPIError`

**Step 5: CRUD Operations** (2 hours)
- Create `app/crud/session.py` with:
  - `create_session()`
  - `get_session()`, `get_session_by_room_code()`
  - `get_sessions_by_teacher()`, `get_sessions_by_student()`
  - `update_session()`, `delete_session()`
  - `add_participant()`, `update_participant_status()`
  - `get_session_participants()`
  - `generate_room_code()` helper

**Step 6: API Endpoints** (3 hours)
- Create `app/api/v1/endpoints/sessions.py` with:
  - `POST /sessions` - Create session
  - `GET /sessions/{id}` - Get session details
  - `GET /sessions` - List user's sessions
  - `PATCH /sessions/{id}` - Update session
  - `DELETE /sessions/{id}` - Delete session
  - `POST /sessions/{id}/join` - Join session
  - `POST /sessions/{id}/leave` - Leave session
  - `POST /sessions/join-by-code` - Join by room code
  - `GET /sessions/{id}/participants` - List participants
- Update `app/api/v1/router.py` to include sessions router
- Fix commented endpoints if needed

**Step 7: Database Migration** (30 min)
- Run `alembic revision --autogenerate -m "add session tables"`
- Review migration
- Run `alembic upgrade head`

**Step 8: Manual Testing** (1 hour)
- Start server with `uvicorn app.main:app --reload`
- Test endpoints via Swagger UI at http://localhost:8000/docs
- Verify Daily.co integration with actual API calls

### Week 2: Frontend Integration Guide

**Frontend Requirements**:
1. Install `@daily-co/daily-js`: `npm install @daily-co/daily-js`
2. Create session creation form (teacher)
3. Create join session form (student)
4. Embed Daily.co iframe or call object

**Teacher Component Flow**:
```javascript
// 1. Create session
const response = await fetch('/api/v1/sessions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Python 101',
    description: 'Lesson 1',
    max_participants: 30
  })
});
const session = await response.json();

// 2. Display room code to share with students
console.log('Room Code:', session.room_code);

// 3. Join session to get join URL with token
const joinResponse = await fetch(`/api/v1/sessions/${session.id}/join`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${jwtToken}` }
});
const { join_url } = await joinResponse.json();

// 4. Create Daily call frame
import DailyIframe from '@daily-co/daily-js';

const callFrame = DailyIframe.createFrame({
  showLeaveButton: true,
  iframeStyle: {
    width: '100%',
    height: '100vh'
  }
});

// 5. Join room
await callFrame.join({ url: join_url });

// 6. Start screen share (teacher only)
// Button click handler:
await callFrame.startScreenShare();
```

**Student Component Flow**:
```javascript
// 1. Join by room code
const response = await fetch('/api/v1/sessions/join-by-code', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ room_code: 'ABC123' })
});
const { join_url } = await response.json();

// 2. Create and join Daily call frame
import DailyIframe from '@daily-co/daily-js';

const callFrame = DailyIframe.createFrame({
  showLeaveButton: true,
  iframeStyle: {
    width: '100%',
    height: '100vh'
  }
});

await callFrame.join({ url: join_url });

// Screen share is automatically displayed by Daily Prebuilt UI
// Students cannot start screen sharing (controlled by token permissions)
```

## Key Technical Decisions

1. Backend generates short-lived meeting tokens on-demand (not stored)
2. Private rooms: `privacy: "private"`; tokens required to join
3. Session state tracked in DB (scheduled → active → ended)
4. MVP uses Daily Prebuilt UI; custom UI later if needed
5. API key is only on backend; never exposed to frontend

## Security Considerations

- JWT auth required for all endpoints
- Role-based permissions encoded in meeting tokens
- Tokens expire after ~4 hours; room expiration configured
- Webhooks (optional in Phase 1) must be HMAC-verified

## Testing Strategy

- Manual e2e flow for teacher and student
- Swagger testing for all endpoints
- Verify Daily.co room creation and join permissions

## Estimated Timeline
- Backend: 11–12 hours
- Frontend integration: 4–6 hours
- Testing: 2–3 hours
- Total: ~17–21 hours
