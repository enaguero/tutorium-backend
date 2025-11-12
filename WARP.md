# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Running the Application
```bash
# Development server with hot reload
uvicorn app.main:app --reload

# Access points:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Alternative docs: http://localhost:8000/redoc
```

### Database Operations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1
```

### Testing
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/api/v1/test_users.py

# Run with coverage
pytest --cov=app
```

## Architecture Overview

### Project Structure
This is a **FastAPI** backend using **SQLAlchemy ORM** with **PostgreSQL** (production) and **SQLite** (testing). Authentication uses **JWT tokens** with **OAuth2** password flow.

### Layered Architecture

**API Layer** (`app/api/`)
- `deps.py`: Dependency injection for database sessions and authentication
- `v1/router.py`: Main API router aggregating all endpoint routers
- `v1/endpoints/`: Individual endpoint modules (auth, users, etc.)

**Core Layer** (`app/core/`)
- `config.py`: Pydantic Settings managing environment variables
- `security.py`: JWT token creation, password hashing (bcrypt)

**Data Layer**
- `models/`: SQLAlchemy ORM models (database tables)
- `schemas/`: Pydantic models for request/response validation
- `crud/`: Database operations (Create, Read, Update, Delete)
- `db/session.py`: SQLAlchemy engine and session configuration
- `db/base.py`: Declarative base for models

### Authentication Flow
1. User credentials sent to `/api/v1/auth/login`
2. `crud.user.authenticate()` verifies credentials
3. `security.create_access_token()` generates JWT
4. Protected endpoints use `get_current_user()` dependency to validate JWT from `Authorization: Bearer <token>` header
5. JWT payload contains user ID in `sub` claim

### Database Connection
- Production: PostgreSQL via `DATABASE_URL` environment variable
- Testing: SQLite in-memory database with session override in `conftest.py`
- All models inherit from `Base` (must be imported in `db/base.py` for Alembic)

### CRUD Pattern
Each entity follows the pattern:
- `models/<entity>.py`: SQLAlchemy model
- `schemas/<entity>.py`: Pydantic schemas (Base, Create, Update, InDB)
- `crud/<entity>.py`: Functions for database operations (get, create, update, etc.)
- `api/v1/endpoints/<entity>.py`: FastAPI route handlers

### Testing Infrastructure
- `tests/conftest.py` provides fixtures:
  - `db`: Fresh SQLite database for each test
  - `client`: TestClient with database dependency override
- Tests use FastAPI's `TestClient` for endpoint testing
- Database is created/dropped per test for isolation

## Environment Variables
Critical environment variables (see `.env.example`):
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (must be changed in production)
- `BACKEND_CORS_ORIGINS`: JSON array of allowed origins
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT expiration time

## Adding New Features

### New Model/Entity Workflow
1. Create SQLAlchemy model in `app/models/<entity>.py`
2. Import model in `app/db/base.py` (required for Alembic)
3. Create Pydantic schemas in `app/schemas/<entity>.py`
4. Create CRUD operations in `app/crud/<entity>.py`
5. Create endpoint router in `app/api/v1/endpoints/<entity>.py`
6. Register router in `app/api/v1/router.py`
7. Generate migration: `alembic revision --autogenerate -m "add <entity>"`
8. Apply migration: `alembic upgrade head`
9. Create tests in `tests/api/v1/test_<entity>.py`

### Protected Endpoints
Use the `get_current_user` dependency from `app/api/deps.py`:
```python
from app.api.deps import get_current_user

@router.get("/protected")
def protected_route(current_user = Depends(get_current_user)):
    return {"user_id": current_user["id"]}
```
