# NexaAI Security Audit

## Authentication

- JWT authentication implemented.
- Access tokens have an expiration time.
- Passwords are hashed.
- Plaintext passwords are never stored.

## Authorization

- Conversations are scoped by authenticated user ID.
- Cross-user conversation access returns 404.
- Chat endpoints verify conversation ownership.

## Input Validation

- Pydantic validates request payloads.
- Conversation titles have length limits.
- Chat messages have length limits.
- Pagination has bounded limits.

## Secrets

- Secrets are loaded from environment variables.
- `.env` is excluded from Git.
- API keys are not included in Docker images.

## Database

- SQLAlchemy parameterized queries are used.
- Production database should use restricted credentials.
- Database backups are enabled through the managed provider.

## API Security

- HTTPS required in production.
- CORS restricted to trusted frontend origins.
- Security headers configured.
- Authentication required for protected endpoints.

## LLM Security

- API keys are never sent to the LLM.
- LLM output is not treated as trusted executable code.
- Prompt injection is considered a future threat area.
- Tool execution is not enabled in V1.

## Reliability

- LLM timeout configured.
- Database connection pre-ping enabled.
- Provider failures are mapped to safe API errors.

## Dependency Security

- `pip-audit` is used to identify known Python dependency vulnerabilities.

## Docker

- Application container runs as a non-root user.
- Secrets are supplied at runtime.

## Remaining Risks

- Distributed rate limiting is not implemented in V1.
- Advanced prompt-injection defenses are not implemented.
- Token-aware context management is planned for a future version.
- Centralized production observability is not yet implemented.
