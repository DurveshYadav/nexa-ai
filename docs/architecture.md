# NexaAI Architecture

## High-Level Architecture

```text
Client
  |
  | HTTPS / JSON
  v
FastAPI
  |
  +--> Auth Router
  |
  +--> Conversation Router
  |
  +--> Chat Router
            |
            v
        Chat Service
            |
            +--> Context Builder
            |
            +--> AI Service
                      |
                      v
                  LLM Provider

Services
  |
  v
Repositories
  |
  v
PostgreSQL

Request Flow

HTTP Request
     |
     v
Middleware
     |
     v
Router
     |
     v
Dependency
     |
     v
Pydantic Validation
     |
     v
Service
     |
     v
Repository
     |
     v
Database

Authentication Flow

Register
   |
   v
Password Hash
   |
   v
PostgreSQL

Login
   |
   v
Verify Password
   |
   v
JWT Access Token
   |
   v
Protected API

Chat Flow

POST /conversations/{id}/messages
             |
             v
       Authenticate
             |
             v
     Verify ownership
             |
             v
       Load history
             |
             v
      Build AI context
             |
             v
         LLM API
             |
             v
      Save user message
             |
             v
   Save assistant message
             |
             v
        API response

