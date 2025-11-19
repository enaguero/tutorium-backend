# Feature: Screen Sharing in Teaching Sessions

## Overview
Enable teachers to share their device screen with one or multiple students during a live teaching session using Daily.co's video infrastructure. This feature provides the foundation for interactive online tutoring by allowing visual demonstration of concepts, code, documents, and other educational materials in real-time.

## Business Context
Screen sharing is the core feature that differentiates synchronous online teaching from asynchronous learning. It enables:
- Real-time visual instruction
- Interactive problem-solving demonstrations
- Live code reviews and debugging sessions
- Document and presentation sharing
- Software tutorial delivery

## User Personas

### Primary Actors
1. **Teacher** - Initiates and controls screen sharing, hosts the session
2. **Student(s)** - Receive and view the shared screen (1-50 students per session)

### User Stories

**As a Teacher:**
- I want to create a teaching session and receive a room link to share with students
- I want to share my entire screen or specific application window so students can follow along
- I want to control when screen sharing starts and stops
- I want to see which students are currently in the room
- I want to mute/unmute participants if needed

**As a Student:**
- I want to join a session using a room link or code provided by the teacher
- I want to view the teacher's shared screen in high quality
- I want to be able to switch between different view modes (fit to screen, fullscreen)
- I want to see who else is in the session

## Functional Requirements

### Core Functionality

#### FR-1: Session Room Management
- **FR-1.1**: System must integrate with Daily.co API to create room instances
- **FR-1.2**: System must allow a teacher to create a new session room
- **FR-1.3**: System must generate and store Daily.co room URLs and tokens
- **FR-1.4**: System must support multiple students (1-50) joining a single session room
- **FR-1.5**: System must authenticate users before providing room access tokens
- **FR-1.6**: System must track session metadata (teacher, students, timing, status)

#### FR-2: Session Access Control
- **FR-2.1**: Teacher must receive an owner token with full room privileges
- **FR-2.2**: Students must receive participant tokens with limited privileges
- **FR-2.3**: Room URLs must be secured and expire after session ends
- **FR-2.4**: System must validate user identity before generating access tokens
- **FR-2.5**: System must support room access via shareable link or room code

#### FR-3: Screen Sharing Initiation
- **FR-3.1**: Only the teacher (session host) can initiate screen sharing
- **FR-3.2**: Teacher must be able to select between:
  - Entire screen (all monitors if multiple)
  - Specific application window
  - Browser tab (for web-based content)
- **FR-3.3**: Teacher must have controls to start/stop screen sharing
- **FR-3.4**: System must display screen share to all participants automatically

#### FR-4: Student Viewing Experience
- **FR-4.1**: Students must receive the screen share stream with minimal latency
- **FR-4.2**: Students must have view controls provided by Daily.co interface
- **FR-4.3**: Students must see connection quality indicators
- **FR-4.4**: System must display participant count to all users
- **FR-4.5**: Students can enable fullscreen mode for better viewing

#### FR-5: Session State Management
- **FR-5.1**: System must track session lifecycle (scheduled → active → ended)
- **FR-5.2**: System must handle participant join/leave events
- **FR-5.3**: System must end session and cleanup Daily.co room when teacher leaves
- **FR-5.4**: System must maintain session history for analytics and troubleshooting
- **FR-5.5**: Rooms must automatically expire after maximum duration (configurable, default 4 hours)

## Technical Architecture

### Integration with Daily.co

Daily.co provides:
- WebRTC infrastructure and global mesh network
- Room creation and management API
- Pre-built UI components (optional)
- Token-based access control
- Screen sharing capabilities built-in
- Recording features (optional)
- Real-time events via webhooks

### Backend Components

#### 1. Session Service (`app/services/session.py`)
Responsibilities:
- Create and manage session records in database
- Interface with Daily.co API for room operations
- Generate access tokens for participants
- Handle session lifecycle events

#### 2. Daily.co Integration Service (`app/services/daily.py`)
Responsibilities:
- Wrapper for Daily.co REST API
- Room creation with custom properties
- Meeting token generation (owner vs participant)
- Webhook event processing
- Room deletion and cleanup

#### 3. Webhook Handler (`app/api/v1/endpoints/webhooks.py`)
Responsibilities:
- Receive Daily.co event notifications
- Process participant join/leave events
- Update session state based on room events
- Handle recording events (future)

### Data Models

#### Session Room
```python
class Session(Base):
    id: UUID (primary key)
    teacher_id: UUID (FK to User)
    title: str (max 200 chars)
    description: str (optional)
    status: Enum (scheduled, active, ended, cancelled)
    
    # Daily.co integration fields
    daily_room_name: str (unique, Daily room identifier)
    daily_room_url: str (full Daily.co room URL)
    
    # Timing
    scheduled_start: datetime (nullable)
    actual_start: datetime (nullable)
    ended_at: datetime (nullable)
    
    # Settings
    max_participants: int (default 50)
    enable_recording: bool (default False)
    enable_chat: bool (default True)
    
    # Metadata
    created_at: datetime
    updated_at: datetime
```

#### Session Participant
```python
class SessionParticipant(Base):
    id: UUID (primary key)
    session_id: UUID (FK to Session)
    user_id: UUID (FK to User)
    role: Enum (teacher, student)
    
    # Access token (stored hashed or not stored)
    daily_token: str (nullable, encrypted)
    
    # Timing
    joined_at: datetime (nullable)
    left_at: datetime (nullable)
    
    # Status
    connection_status: Enum (invited, joined, left, kicked)
    
    created_at: datetime
```

#### Session Event Log
```python
class SessionEvent(Base):
    id: UUID (primary key)
    session_id: UUID (FK to Session)
    event_type: str (participant_joined, participant_left, 
                      screen_share_started, screen_share_stopped, etc.)
    user_id: UUID (FK to User, nullable)
    event_data: JSON (additional event details)
    timestamp: datetime
```

### API Endpoints

#### Session Management
```
POST   /api/v1/sessions
  Body: {
    "title": "Python 101 - Lesson 1",
    "description": "Introduction to variables",
    "scheduled_start": "2025-11-20T10:00:00Z",
    "max_participants": 30
  }
  Response: {
    "id": "uuid",
    "title": "...",
    "daily_room_url": "https://tutorium.daily.co/room-name",
    "teacher_join_url": "...", (with token embedded)
    "room_code": "ABC123" (shareable code)
  }

GET    /api/v1/sessions/{id}
  Response: {
    "id": "uuid",
    "title": "...",
    "status": "active",
    "teacher": {...},
    "participant_count": 12,
    "created_at": "...",
    ...
  }

PATCH  /api/v1/sessions/{id}
  Body: {"status": "ended"} or {"title": "..."}
  
DELETE /api/v1/sessions/{id}
  (Ends session and deletes Daily.co room)

GET    /api/v1/sessions
  Query: ?status=active&teacher_id=uuid
  Response: List of sessions

GET    /api/v1/sessions/{id}/participants
  Response: [
    {
      "user_id": "...",
      "name": "...",
      "role": "student",
      "joined_at": "...",
      "connection_status": "joined"
    },
    ...
  ]
```

#### Joining Sessions
```
POST   /api/v1/sessions/{id}/join
  Body: {} (user from JWT token)
  Response: {
    "join_url": "https://tutorium.daily.co/room?t=token",
    "room_name": "room-name",
    "token": "meeting-token"
  }

POST   /api/v1/sessions/join-by-code
  Body: {"room_code": "ABC123"}
  Response: {
    "session_id": "uuid",
    "join_url": "...",
    ...
  }

POST   /api/v1/sessions/{id}/leave
  Body: {} (user from JWT token)
  Response: {"success": true}
```

#### Webhooks (Daily.co → Backend)
```
POST   /api/v1/webhooks/daily
  Body: Daily.co webhook payload
  Events handled:
    - room.created
    - room.deleted
    - participant.joined
    - participant.left
    - screen-share.started
    - screen-share.stopped
```

### Daily.co API Integration

#### Configuration
```python
# app/core/config.py
class Settings(BaseSettings):
    DAILY_API_KEY: str
    DAILY_DOMAIN: str = "tutorium.daily.co"  # Your custom domain
    DAILY_WEBHOOK_SECRET: str
```

#### Key Operations

**1. Create Room**
```
POST https://api.daily.co/v1/rooms
Headers: Authorization: Bearer {DAILY_API_KEY}
Body: {
  "name": "session-{uuid}",
  "privacy": "private",
  "properties": {
    "max_participants": 50,
    "enable_screenshare": true,
    "enable_chat": true,
    "enable_recording": "cloud",
    "start_video_off": true,
    "start_audio_off": false,
    "exp": 1700000000  (Unix timestamp for expiration)
  }
}
```

**2. Create Meeting Token**
```
POST https://api.daily.co/v1/meeting-tokens
Headers: Authorization: Bearer {DAILY_API_KEY}
Body: {
  "properties": {
    "room_name": "session-{uuid}",
    "user_name": "John Doe",
    "is_owner": true,  (for teacher)
    "enable_screenshare": true,  (only for teacher)
    "exp": 1700000000,
    "user_id": "user-uuid"
  }
}
```

**3. Delete Room**
```
DELETE https://api.daily.co/v1/rooms/{room_name}
Headers: Authorization: Bearer {DAILY_API_KEY}
```

### Frontend Integration

#### Embedding Daily.co

**Option 1: Daily Prebuilt (Recommended for MVP)**
- Use Daily's pre-built UI component
- Minimal frontend code required
- Full-featured interface out of the box

```javascript
// React example
import DailyIframe from '@daily-co/daily-js';

const callFrame = DailyIframe.createFrame({
  showLeaveButton: true,
  iframeStyle: {
    width: '100%',
    height: '100vh',
  }
});

callFrame.join({ url: joinUrl });
```

**Option 2: Daily Call Object (Custom UI)**
- Full control over UI/UX
- More development effort
- Better brand integration

```javascript
import DailyIframe from '@daily-co/daily-js';

const daily = DailyIframe.createCallObject();
daily.join({ url: joinUrl, token: meetingToken });

// Listen to events
daily.on('participant-joined', handleParticipantJoined);
daily.on('screen-share-started', handleScreenShareStarted);

// Start screen share
daily.startScreenShare();
```

### Security Implementation

#### Token-Based Access
- Backend generates meeting tokens via Daily.co API
- Tokens include user identity and permissions
- Teacher tokens have `is_owner: true` and `enable_screenshare: true`
- Student tokens have limited permissions
- Tokens expire after session duration

#### Webhook Verification
```python
# Verify Daily.co webhooks
import hmac
import hashlib

def verify_daily_webhook(request_body: bytes, signature: str) -> bool:
    expected = hmac.new(
        DAILY_WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

## Non-Functional Requirements

#### NFR-1: Performance
- Leverage Daily.co's 13ms median first-hop latency
- Support 50 concurrent students per session
- Backend API response time < 200ms

#### NFR-2: Scalability
- Backend supports 100+ concurrent sessions
- Daily.co handles all WebRTC infrastructure scaling
- Stateless backend design for horizontal scaling

#### NFR-3: Reliability
- 99.5% backend uptime
- Daily.co provides 99.99% service uptime
- Graceful error handling for Daily.co API failures
- Session recovery on temporary backend failures

#### NFR-4: Security
- HTTPS/TLS for all API communication
- JWT authentication for backend API
- Daily.co provides end-to-end encryption for media
- Meeting tokens with expiration
- Webhook signature verification
- No storage of sensitive tokens in logs

#### NFR-5: Cost Optimization
- Monitor Daily.co usage (minutes per month)
- Implement auto-cleanup of unused rooms
- Set appropriate room expiration times
- Use Daily.co developer tier for testing

## User Interface Requirements

### Teacher Flow
1. **Create Session**
   - Form: Title, description, scheduled time
   - Click "Create Session"
   - Receive shareable room link/code

2. **Start Session**
   - Click "Join Room" or "Start Session"
   - Embedded Daily.co interface loads
   - Click "Share Screen" button in Daily UI
   - Select screen/window to share

3. **During Session**
   - See participant list (Daily UI)
   - Control screen sharing (start/stop/pause)
   - Monitor connection quality
   - End session when done

### Student Flow
1. **Join Session**
   - Receive link/code from teacher
   - Click link or enter code on platform
   - Backend validates and provides join URL with token
   - Redirected to Daily.co room

2. **View Session**
   - See teacher's screen share automatically
   - View controls (fullscreen, layout options)
   - See other participants
   - Leave when done

## Implementation Phases

### Phase 1: MVP (Week 1-2)
**Backend:**
- Daily.co API integration service
- Session CRUD endpoints
- Meeting token generation
- Basic webhook handling

**Frontend:**
- Session creation form (teacher)
- Join session by link (student)
- Daily Prebuilt iframe integration
- Simple session list view

**Deliverables:**
- Teacher can create sessions
- Students can join via link
- Screen sharing works via Daily UI
- Basic participant tracking

### Phase 2: Enhanced Management (Week 3)
**Backend:**
- Session event logging
- Participant status tracking
- Room code generation and lookup
- Admin controls (end session, kick participant)

**Frontend:**
- Session dashboard for teachers
- Active session indicators
- Participant list with status
- Room code input for students

### Phase 3: Polish & Production (Week 4)
**Backend:**
- Automated room cleanup
- Usage analytics and monitoring
- Error handling and retry logic
- Rate limiting and abuse prevention

**Frontend:**
- Session history
- Improved UX/UI
- Error states and loading indicators
- Mobile responsive design

## Dependencies & Prerequisites

### External Services
- **Daily.co Account**: Sign up at https://www.daily.co/
- **Daily.co API Key**: Generate from dashboard
- **Daily.co Domain**: Custom domain (e.g., `tutorium.daily.co`)

### Python Packages
```
# Add to requirements.txt
httpx>=0.24.0          # For Daily.co API calls
python-jose[cryptography]>=3.3.0  # For token handling
```

### Environment Variables
```
DAILY_API_KEY=your_api_key_here
DAILY_DOMAIN=your_domain.daily.co
DAILY_WEBHOOK_SECRET=your_webhook_secret
```

## Success Metrics

### Key Performance Indicators
1. **Technical Metrics**
   - Session creation success rate > 99%
   - Join success rate > 95%
   - Average API response time < 200ms

2. **User Engagement**
   - Average session duration
   - Number of active sessions per day
   - Students per session (average)
   - Return rate for teachers

3. **Quality Metrics**
   - Daily.co connection success (tracked by Daily)
   - Screen share success rate
   - User satisfaction (post-session survey)

## Cost Estimation

### Daily.co Pricing (as of 2024)
- **Developer Tier**: Free, 10K minutes/month
- **Starter**: $9/month for 100K minutes
- **Scale**: Custom pricing for higher volumes

### Usage Calculation
- Example: 100 sessions/day × 30 days = 3,000 sessions/month
- Average 30 minutes per session = 90,000 minutes/month
- Estimated cost: ~$9/month (Starter tier)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Daily.co service outage | Complete feature unavailability | Monitor status page, implement status checks, communicate with users |
| API rate limits | Session creation failures | Implement rate limiting, caching, and queuing |
| Cost overruns | Budget exceeded | Set usage alerts, implement session time limits, monitor metrics |
| Token security | Unauthorized access | Short token expiry, HTTPS only, no token logging |
| User confusion with Daily UI | Poor UX | Provide onboarding tutorial, clear instructions |

## Future Enhancements
- **Two-way video/audio**: Enable video conferencing mode
- **Session recording**: Store sessions for later review
- **Breakout rooms**: Split large classes into groups
- **Interactive whiteboard**: Annotation tools via Daily add-ons
- **Chat integration**: Use Daily's chat or custom solution
- **Mobile apps**: Native iOS/Android with Daily SDKs
- **Session scheduling**: Calendar integration
- **Analytics dashboard**: Detailed usage and engagement metrics
- **Co-teaching**: Multiple teachers per session
