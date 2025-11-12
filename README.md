# Tutorium Backend API

FastAPI backend for Tutorium application.

## Setup

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database (after setting up Alembic):
```bash
alembic upgrade head
```

## Running the server

Development:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Testing

```bash
pytest
```

## Project Structure

```
app/
├── api/              # API routes
│   ├── deps.py       # Dependencies (DB, auth)
│   └── v1/           # API version 1
├── core/             # Core settings
├── crud/             # Database operations
├── db/               # Database configuration
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
└── utils/            # Utility functions
```
