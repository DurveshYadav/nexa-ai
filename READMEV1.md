# NexaAI

NexaAI is a production-style AI Assistant REST API built with Python and FastAPI.

## V1 Goals

- FastAPI REST API
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- LLM Integration
- Conversation Context
- Testing
- Docker
- CI/CD
- Deployment

## Architecture

Client
→ FastAPI
→ Service
→ Repository
→ PostgreSQL

Chat:

Client
→ FastAPI
→ Chat Service
→ AI Service
→ LLM

## Local Setup

### 1. Clone

git clone <repository-url>
cd nexa-ai

python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

alembic upgrade head
uvicorn app.main:app --reload

### API:
http://localhost:8000

### Swagger:
http://localhost:8000/docs


---

# Document Docker
## Docker
Build and start:
docker compose up --build -d
docker compose ps
docker compose logs -f api
docker compose exec api alembic upgrade head
docker compose exec api alembic upgrade head
docker compose down -v

# API Reference
Base URL:
/api//helth
# Response
{
  "status": "healthy"
}


