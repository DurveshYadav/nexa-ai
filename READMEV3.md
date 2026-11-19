# NexaAI — AI Engineering Platform

NexaAI is an evolving AI engineering project built with Python and FastAPI. It brings together conversational AI, machine learning prediction APIs, and tool-using AI agents in one versioned repository.

The project demonstrates how to design, build, test, secure, and deploy practical AI-powered backend systems.

## Project Versions

| Version | Project | Description |
|---|---|---|
| V1 | AI Assistant API | Authentication, conversations, chat and LLM integration |
| V2 | Intelligence API | Machine learning prediction API |
| V3 | Support Agent | Tool calling, orchestration, permissions and human approvals |
| V4 | RAG Platform | Planned document retrieval and knowledge-based responses |
| V5 | Autonomous Agent Platform | Planned advanced agent workflows and integrations |

## NexaAI V3 — AI-Powered Customer Support Agent

NexaAI V3 is a tool-using customer support agent built with Python, FastAPI and an LLM provider.

Unlike a traditional chatbot, the agent can interact with business services through structured tool calling. Backend services validate and execute the requested operations under authenticated user context and permission controls.

### Key Features

- LLM-powered customer support conversations
- Structured tool/function calling
- Centralized tool registry and execution engine
- Multi-step agent orchestration
- JWT-based authentication
- Customer-level authorization and ownership checks
- Human-in-the-loop approval workflows
- Agent run tracking and execution history
- Approval execution state management
- PostgreSQL persistence
- Structured application logging and request correlation
- Automated tests and Docker support

### Business Use Cases

- Retrieve order status and order details
- Retrieve product information
- Check product availability
- Retrieve customer profile information
- Create support tickets
- Check refund eligibility
- Approval-controlled order cancellation and refund requests

## Architecture

```mermaid
flowchart TD
    A[Client / API Consumer] --> B[FastAPI Application]

    B --> V1[V1 Assistant API]
    B --> V2[V2 ML API]
    B --> V3[V3 Agent API]

    V3 --> AS[Agent Service]
    AS --> O[Agent Orchestrator]
    O --> L[LLM Provider]
    O --> R[Tool Registry]
    R --> E[Tool Executor]

    E --> S[Business Services]
    S --> DB[(PostgreSQL)]

    O --> RM[Run Manager]
    O --> AP[Approval Service]
    AP --> DB
    RM --> DB
```

### V3 Component Responsibilities

| Component | Responsibility |
|---|---|
| API layer | HTTP requests, authentication and validation |
| Agent service | Coordinates the support-agent workflow |
| Orchestrator | Manages the LLM/tool execution loop |
| LLM provider | Communicates with the configured LLM |
| Tool registry | Defines available tools and their schemas |
| Tool executor | Validates and executes tool calls |
| Business services | Handle order, product, customer and support operations |
| Authorization service | Builds trusted execution context and permissions |
| Approval service | Manages sensitive-action approvals |
| Run manager | Tracks agent run status and execution history |
| Repositories | Encapsulate database access |

**Security principle:** The LLM proposes actions; backend code validates permissions, resource ownership, business rules and approval requirements.

## Technology Stack

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- OpenAI API integration
- Pytest
- Docker and Docker Compose
- GitHub Actions

Redis is a possible future infrastructure addition; it is not currently required by the implemented application.

## Project Structure

```text
nexa-ai/
├── app/
│   ├── ai/
│   ├── api/
│   │   ├── v1/
│   │   ├── v2/
│   │   └── v3/
│   ├── core/
│   ├── database/
│   ├── integrations/
│   │   └── llm/
│   ├── middleware/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   │   └── v3/
│   └── tools/
│       └── v3/
├── alembic/
│   └── versions/
├── tests/
├── ml/
├── .github/
│   └── workflows/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements-2.txt
└── README.md
```

## Installation and Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd nexa-ai
```

### 2. Create a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements-2.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Configure the required values in `.env`:

```dotenv
APP_NAME=NexaAI
APP_VERSION=1.0.0
DEBUG=false

DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/nexaai

JWT_SECRET_KEY=replace_with_a_secure_random_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

OPENAI_API_KEY=your_llm_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TIMEOUT=30

CHAT_CONTEXT_MESSAGES=20
LOG_LEVEL=INFO
```

Use your actual database credentials and configured LLM model. Never commit `.env` or real credentials.

### 5. Run database migrations

Make sure PostgreSQL is running and the configured database exists.

```bash
alembic upgrade head
```

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

The default local API address is:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

## API Reference

All API versions are registered in the same FastAPI application.

### V1 — Assistant API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a user |
| POST | `/api/v1/auth/login` | Authenticate and obtain a token |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/conversations` | Create conversation |
| GET | `/api/v1/conversations` | List conversations |
| GET | `/api/v1/conversations/{conversation_id}` | Get conversation |
| PATCH | `/api/v1/conversations/{conversation_id}` | Update conversation |
| DELETE | `/api/v1/conversations/{conversation_id}` | Delete conversation |
| GET | `/api/v1/conversations/{conversation_id}/messages` | Retrieve message history |
| POST | `/api/v1/conversations/{conversation_id}/messages` | Send a message |
| POST | `/api/v1/ai/test` | Test LLM integration |

### V2 — Intelligence API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v2/ml/predict` | Predict customer churn |

Consult the generated OpenAPI documentation for the exact prediction request and response schemas.

### V3 — Support Agent API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v3/agent/chat` | Send a message to the agent |
| GET | `/api/v3/agent/runs/{run_id}` | Retrieve run status |
| GET | `/api/v3/agent/runs/{run_id}/history` | Retrieve execution history |
| GET | `/api/v3/agent/approvals/{approval_id}` | Retrieve approval details |
| POST | `/api/v3/agent/approvals/{approval_id}/confirm` | Approve or reject an action |
| POST | `/api/v3/agent/approvals/{approval_id}/execute` | Execute an approved action |

### V3 Chat Example

Request:

```json
{
  "message": "Please check the status of my order."
}
```

Optional existing conversation:

```json
{
  "message": "Please check the status of my order.",
  "conversation_id": 12
}
```

Response structure:

```json
{
  "run_id": "generated-run-id",
  "conversation_id": 12,
  "status": "completed",
  "message": "Agent response",
  "approval_id": null
}
```

The response status can be `completed`, `failed` or `approval_required`.

### V3 Approval Workflow

Sensitive operations require explicit approval before execution.

1. The agent identifies an action requiring approval.
2. The backend creates an approval record.
3. The authenticated user retrieves approval details.
4. The user approves or rejects the action.
5. The backend revalidates permissions and tool availability.
6. The approved action is atomically claimed and executed.
7. The execution result is persisted.

Approval execution states include `executing`, `executed`, `execution_failed` and `execution_unknown`.

An uncertain execution outcome must be reconciled rather than blindly retried.

## Authentication and Authorization

Protected API endpoints use JWT authentication.

V3 execution context is constructed using trusted backend information, including:

- Authenticated user ID
- Mapped customer ID
- Conversation ID
- Run ID
- Request ID
- Authorized permissions

The agent must not trust user-supplied customer identity or LLM-generated permission decisions.

## Error Handling

V3 uses structured tool and execution error codes, including:

| Error code | Meaning |
|---|---|
| `UNKNOWN_TOOL` | Tool does not exist |
| `TOOL_NOT_ALLOWED` | Tool is not permitted |
| `INVALID_ARGUMENTS` | Invalid tool arguments |
| `PERMISSION_DENIED` | Required permission is missing |
| `APPROVAL_REQUIRED` | Human approval is required |
| `APPROVAL_EXPIRED` | Approval has expired |
| `MAX_ITERATIONS_EXCEEDED` | Agent iteration limit reached |
| `LLM_PROVIDER_ERROR` | LLM provider failure |
| `EXECUTION_ERROR` | Tool execution failure |

HTTP errors and domain-level tool errors may use different response structures. Refer to `/docs` and the implementation for the exact API error contract.

## Database and Migrations

NexaAI uses PostgreSQL for persistent application data.

SQLAlchemy manages ORM models, while Alembic manages database schema migrations.

Useful commands:

```bash
# Current revision
alembic current

# Migration history
alembic history

# Migration heads
alembic heads

# Check model/migration consistency
alembic check

# Apply migrations
alembic upgrade head
```

Run migration checks against a development or test database before production deployment.

## Running Tests

Run the complete test suite:

```bash
pytest -q
```

Run V3-specific tests:

```bash
pytest -q tests/test_v3_*.py
```

Compile the application and tests:

```bash
python -m compileall -q app tests
```

Check whitespace errors:

```bash
git diff --check
```

## Docker

Configure the required environment variables in `.env` before starting Docker Compose.

Build and start:

```bash
docker compose up --build -d
```

Check service status:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs -f api
```

View PostgreSQL logs:

```bash
docker compose logs -f postgres
```

The API container is configured to run Alembic migrations before starting Uvicorn.

Stop containers:

```bash
docker compose down
```

**Warning:** `docker compose down -v` deletes the Compose-managed database volume. Use it only when intentionally resetting local database data.

## Observability

The application includes:

- Configurable application logging
- Request correlation IDs
- Request completion and failure logs
- Request duration measurement
- Agent run lifecycle logs
- Tool execution duration and failure logs
- LLM request latency and token usage logs
- Approval lifecycle logs

The request middleware exposes the request ID in the `X-Request-ID` response header.

## Security Considerations

- Use strong JWT secrets and appropriate token expiry.
- Keep secrets in environment variables or a dedicated secret manager.
- Never commit `.env` files or API keys.
- Enforce authentication on protected endpoints.
- Enforce user and customer ownership checks.
- Validate tool names and arguments.
- Enforce backend permission checks.
- Require explicit approval for sensitive actions.
- Protect approval execution against duplicate claims.
- Treat user input, LLM output and tool results as untrusted.
- Avoid exposing internal exception details or sensitive data in logs.
- Use database backups and test restoration procedures.

The LLM is never the security authority. The backend must enforce every security decision.

## CI/CD

The project includes a GitHub Actions workflow under:

```text
.github/workflows/ci.yml
```

The CI workflow is configured to run automated checks, database migrations, tests and a Docker image build.

Review the workflow file for the exact branches and execution conditions.

## Deployment Architecture

A future AWS deployment can use:

- Amazon ECS Fargate for API containers
- Amazon ECR for container images
- Amazon RDS for PostgreSQL
- Application Load Balancer for HTTP routing
- AWS Secrets Manager for credentials
- Amazon CloudWatch for logs and monitoring

Actual cloud deployment, scaling, backups, alerting and production hardening require separate configuration and verification.

## Future Improvements

- V4: Retrieval-Augmented Generation (RAG)
- Document ingestion and chunking
- Embeddings and vector search
- Retrieval evaluation and reranking
- V5: Multi-agent workflows
- LangGraph and MCP integrations
- Redis for appropriate caching and transient state
- Distributed tracing and advanced metrics
- Production cloud deployment and observability

## Learning Outcomes

Through NexaAI, the project demonstrates practical experience with:

- REST API design
- Authentication and authorization
- Relational database design
- Machine learning API integration
- LLM integration and structured tool calling
- Agent orchestration
- Human-in-the-loop workflows
- Secure tool execution
- Automated testing
- Docker and CI/CD
- Application observability

## License

A license has not yet been added to this repository. Add a `LICENSE` file before declaring the project open source.

---

**NexaAI — Building practical AI systems, one version at a time.**
