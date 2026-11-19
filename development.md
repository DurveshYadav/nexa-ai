# Development Guide

## Requirements

- Python 3.12+
- PostgreSQL
- Docker
- Docker Compose

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| DATABASE_URL | Yes | PostgreSQL connection |
| OPENAI_API_KEY | Yes | LLM provider API key |
| OPENAI_MODEL | Yes | Model used by NexaAI |
| OPENAI_TIMEOUT | No | LLM timeout |
| CHAT_CONTEXT_MESSAGES | No | Number of historical messages |
