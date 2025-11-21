# Tutorium Backend - Implementation Plan

## Overview
This document outlines the implementation order and priorities for all Tutorium backend features. Each feature is documented in detail in the `docs/features/` directory.

## Project Information
- **Framework**: FastAPI
- **Database**: PostgreSQL (production), SQLite (testing)
- **ORM**: SQLAlchemy
- **Authentication**: JWT with OAuth2
- **Architecture**: Layered (API → Core → CRUD → Models)

---

## Implementation Phases

### Phase 1: Foundation (Completed)
**Status**: ✅ Complete

#### 1.1 Core Authentication & User Management
- User registration and login
- JWT token authentication
- Password hashing with bcrypt
- User CRUD operations
- Protected endpoints

**Files**:
- `app/models/user.py`
- `app/schemas/user.py`
- `app/crud/user.py`
- `app/api/v1/endpoints/auth.py`
- `app/api/v1/endpoints/users.py`

---

### Phase 2: Teaching Sessions with Screen Sharing (Current)
**Status**: 🚧 In Progress (25% complete - 2/8 steps)  
**Priority**: P0 (Critical)  
**Estimated Time**: 4 weeks  
**Feature Doc**: [`docs/features/01-screen-sharing.md`](features/01-screen-sharing.md)

**Progress**:
- ✅ Step 1: Environment Setup (PR #2)
- ✅ Step 2: Database Models (PR #3)
- ⏳ Step 3: Pydantic Schemas (IN PROGRESS)
- ⏳ Step 4-8: Pending

#### 2.1 Overview
Enable teachers to create virtual rooms and share their screen with one or multiple students using Daily.co's WebRTC infrastructure.

#### 2.2 Implementation Steps

**Step 1: Environment Setup** ✅ COMPLETED (PR #2)
- ✅ Add Daily.co config to `app/core/config.py`
- ✅ Update `.env.example` with Daily.co vars
- ✅ Create setup guide: `docs/DAILY_SETUP.md`
- ⏳ Get Daily.co API key (user action required)

**Step 2: Database Models** ✅ COMPLETED (PR #3)
- ✅ Session model (daily_room_name: 255, daily_room_url: 512)
- ✅ SessionParticipant model (role, connection status)
- ✅ SessionEvent model (audit log)
- ✅ User model updates (relationships)

3. Pydantic schemas
   - Session create/update/response schemas
   - Participant schemas
   - Join session schemas

4. CRUD operations
   - Session CRUD (create, read, update, delete)
   - Participant management
   - Room code generation and lookup

5. API endpoints
   - `POST /api/v1/sessions` - Create session
   - `GET /api/v1/sessions/{id}` - Get session details
   - `GET /api/v1/sessions` - List user's sessions
   - `PATCH /api/v1/sessions/{id}` - Update session
   - `DELETE /api/v1/sessions/{id}` - Delete session
   - `POST /api/v1/sessions/{id}/join` - Join session
   - `POST /api/v1/sessions/{id}/leave` - Leave session
   - `POST /api/v1/sessions/join-by-code` - Join by room code
   - `GET /api/v1/sessions/{id}/participants` - List participants

6. Database migration
   - Create and apply Alembic migration

**Week 2: Webhooks & Real-time Events**
1. Webhook endpoint
   - `POST /api/v1/webhooks/daily` - Receive Daily.co events
   - Webhook signature verification
   - Event processing logic

2. Event handling
   - participant.joined
   - participant.left
   - screen-share.started
   - screen-share.stopped

3. Event logging
   - Store events in SessionEvent table
   - Provide event history endpoint

**Week 3: Enhanced Features**
1. Session state management
   - Auto-update session status
   - Handle reconnections
   - Participant status tracking

2. Room management
   - Auto-cleanup expired rooms
   - Background task for cleanup
   - Usage tracking

3. Access control improvements
   - Verify participant permissions
   - Rate limiting for session creation
   - Validation improvements

**Week 4: Testing & Production**
1. Unit tests
   - CRUD operations
   - Daily.co client mocking
   - Schema validation

2. Integration tests
   - API endpoint testing
   - Session lifecycle testing
   - Webhook handling

3. Documentation
   - API documentation review
   - Update README with setup instructions
   - Environment variable documentation

4. Deployment preparation
   - Environment configuration
   - Error monitoring setup
   - Performance optimization

#### 2.3 Implementation Guide
See [`docs/features/01-screen-sharing-implementation.md`](features/01-screen-sharing-implementation.md) for detailed FastAPI implementation steps with code examples.

#### 2.4 Dependencies
- Daily.co account and API key
- `httpx` library (already in requirements.txt)
- Environment variables: `DAILY_API_KEY`, `DAILY_DOMAIN`, `DAILY_WEBHOOK_SECRET`

#### 2.5 Success Criteria
- ✅ Teachers can create sessions and receive shareable room links
- ✅ Students can join sessions via link or room code
- ✅ Daily.co integration works (room creation, token generation)
- ✅ Screen sharing functionality available in Daily.co UI
- ✅ Participant tracking works
- ✅ Webhooks process events correctly
- ✅ 95%+ test coverage for new code
- ✅ API documented in Swagger/ReDoc

---

### Phase 3: Session History & Analytics (Future)
**Status**: 📋 Planned  
**Priority**: P1 (High)  
**Estimated Time**: 2 weeks

#### 3.1 Features
- View past sessions
- Session duration tracking
- Participant attendance records
- Usage statistics for teachers
- Export session data

#### 3.2 Requirements
- Session history endpoints
- Analytics aggregation
- Report generation
- Data export functionality

---

### Phase 4: Session Recording (Future)
**Status**: 📋 Planned  
**Priority**: P2 (Medium)  
**Estimated Time**: 2 weeks  
**Dependency**: Phase 2 complete

#### 4.1 Features
- Optional session recording via Daily.co
- Recording storage (cloud)
- Recording playback
- Recording access control
- Recording deletion

#### 4.2 Requirements
- Daily.co recording API integration
- Recording metadata storage
- Storage management
- Consent handling
- Privacy controls

---

### Phase 5: Chat & Messaging (Future)
**Status**: 📋 Planned  
**Priority**: P2 (Medium)  
**Estimated Time**: 2 weeks

#### 5.1 Features
- Real-time chat during sessions
- Direct messages between users
- Chat history
- File sharing in chat

#### 5.2 Requirements
- WebSocket implementation
- Message storage
- File upload handling
- Notification system

---

### Phase 6: Scheduling & Calendar Integration (Future)
**Status**: 📋 Planned  
**Priority**: P2 (Medium)  
**Estimated Time**: 2 weeks

#### 6.1 Features
- Schedule future sessions
- Calendar view for teachers
- Student availability
- Automated reminders
- iCal export

#### 6.2 Requirements
- Scheduling logic
- Calendar API
- Email/notification service
- Timezone handling

---

### Phase 7: Payment & Billing (Future)
**Status**: 📋 Planned  
**Priority**: P3 (Low)  
**Estimated Time**: 3 weeks

#### 7.1 Features
- Payment integration (Stripe)
- Session pricing
- Teacher payouts
- Transaction history
- Invoicing

#### 7.2 Requirements
- Stripe API integration
- Payment models
- Transaction tracking
- Payout logic
- Tax handling

---

## Development Workflow

### Starting a New Feature
1. Review feature documentation in `docs/features/`
2. Create feature branch: `git checkout -b feature/feature-name`
3. Implement in order:
   - Database models
   - Pydantic schemas
   - CRUD operations
   - API endpoints
   - Tests
4. Create database migration: `alembic revision --autogenerate -m "description"`
5. Run tests: `pytest`
6. Update API documentation
7. Create pull request

### Code Review Checklist
- [ ] Follows existing project structure
- [ ] All tests pass
- [ ] Migration tested
- [ ] API endpoints documented
- [ ] Error handling implemented
- [ ] Authentication/authorization checked
- [ ] No sensitive data in logs
- [ ] Code follows PEP 8 style

### Testing Requirements
- Unit test coverage > 80%
- Integration tests for all endpoints
- Test both success and error cases
- Mock external services (Daily.co, etc.)

---

## Technology Decisions

### Why Daily.co?
- Enterprise-grade WebRTC infrastructure
- No need to build custom signaling servers
- Global CDN with low latency (13ms median)
- Built-in screen sharing and recording
- Token-based security
- Comprehensive API and webhooks
- 99.99% uptime SLA
- Free tier for development/testing

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Built-in data validation (Pydantic)
- Modern Python features
- Great developer experience
- Strong typing support

### Why SQLAlchemy?
- Mature and well-tested ORM
- Supports multiple databases
- Good migration support (Alembic)
- Relationships and eager loading
- Raw SQL when needed

---

## Current Focus: Phase 2

**Next Steps**:
1. ✅ Create feature documentation
2. ✅ Design database schema
3. ⏳ Set up Daily.co account and get API credentials
4. ⏳ Implement Daily.co integration service
5. ⏳ Create database models and migration
6. ⏳ Implement CRUD operations
7. ⏳ Build API endpoints
8. ⏳ Add webhook handling
9. ⏳ Write tests
10. ⏳ Deploy to staging

**Track Progress**: Update this document as tasks are completed.

---

## Resources

### Documentation
- [Daily.co API Docs](https://docs.daily.co/reference/rest-api)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

### Internal Docs
- [Feature: Screen Sharing](features/01-screen-sharing.md)
- [Implementation Guide: Screen Sharing](features/01-screen-sharing-implementation.md)
- [WARP.md](../WARP.md) - Development commands and architecture

### Setup Guides
- See `README.md` for initial setup
- See `.env.example` for required environment variables

---

## Notes

### Dependencies Between Phases
- Phase 4 (Recording) requires Phase 2 (Sessions) complete
- Phase 7 (Payments) may depend on Phase 3 (Analytics) for billing data
- Most other phases are independent

### Risk Management
- Daily.co service dependency: Monitor status page, have fallback plan
- Cost scaling: Implement usage limits and monitoring
- Data privacy: Ensure GDPR compliance, especially with recording

### Performance Targets
- API response time: < 200ms (p95)
- Database query time: < 50ms (p95)
- Support 100+ concurrent sessions
- Support 50 students per session

---

**Last Updated**: 2025-11-19  
**Current Phase**: Phase 2 - Teaching Sessions with Screen Sharing  
**Status**: Week 1 - Core Infrastructure
