# NexaAI V3 — Agent Architecture

## 1. Objective

NexaAI V3 introduces a controlled AI Support Agent that can understand
customer requests, select approved tools, execute business operations,
and return responses.

The architecture separates API handling, orchestration, LLM communication,
tool execution, and business logic.

## 2. High-Level Architecture

Client
  |
  v
Agent API
  |
  v
Agent Service
  |
  v
Agent Orchestrator
  |
  +--------------------+
  |                    |
  v                    v
LLM Provider       Tool Executor
                       |
                       v
                  Tool Registry
                       |
                       v
                  Tool Handlers
                       |
                       v
                 Business Services
                       |
                       v
                   Repositories
                       |
                       v
                    Database

## 3. Core Components

### Agent API
- Endpoint: POST /api/v3/agent/chat
- Validates request data.
- Uses existing V1 JWT authentication.
- Passes the authenticated user and request to Agent Service.
- Does not execute tools or contain business logic.

### Agent Service
- Coordinates the agent use case.
- Verifies conversation ownership.
- Loads conversation history.
- Creates trusted execution context.
- Calls Agent Orchestrator.
- Persists relevant messages and results.

### Agent Orchestrator
- Controls the LLM and tool-calling loop.
- Sends conversation context to the LLM Provider.
- Processes tool requests.
- Sends tool results back to the LLM.
- Enforces maximum iterations and execution limits.
- Does not access the database directly.

### LLM Provider
- Provides a provider-independent interface.
- Reuses the existing app/ai/client.py OpenAI client.
- Hides provider-specific SDK details from the orchestrator.

### Tool Registry
- Stores approved tool definitions and schemas.
- Supports tool lookup by name.
- Does not execute tools.

### Tool Executor
- Validates tool names and arguments.
- Uses trusted execution context.
- Checks permissions and approval requirements.
- Dispatches approved tool handlers.
- Normalizes tool results and handles failures.

### Execution Context
- Contains trusted user_id, conversation_id, run_id,
  request_id, and permissions.
- Is created by backend application code.
- Never trusts identity supplied by the LLM.

### Business Services
- Implement actual business operations.
- Apply business rules.
- Use repositories or external integrations.
- Remain independent of LLM provider details.

## 4. Dependency Direction

API -> Agent Service -> Agent Orchestrator
Agent Orchestrator -> LLM Provider
Agent Orchestrator -> Tool Executor
Tool Executor -> Tool Registry
Tool Executor -> Tool Handlers
Tool Handlers -> Business Services
Business Services -> Repositories -> Database

## 5. Existing NexaAI Components to Reuse

- app/api/deps.py: authentication and database dependencies.
- app/ai/client.py: shared OpenAI client.
- app/ai/service.py: existing LLM communication.
- app/models/: existing database models.
- app/repositories/: existing data-access layer.
- app/core/: configuration, exceptions, and logging.

V1 chat behavior and V2 ML functionality remain independent.

## 6. Security Boundaries

- The backend determines the authenticated user identity.
- Conversation ownership is checked before agent execution.
- Only registered tools can execute.
- Tool arguments are validated before execution.
- Sensitive operations require approval.
- The LLM cannot directly access repositories or the database.
- Tool failures must never be reported as successful operations.

## 7. Initial Architecture Decisions

- Use a controlled tool-using agent.
- Start with a custom Python orchestration loop.
- Reuse the existing OpenAI client through an adapter.
- Use explicit tool registration and Pydantic validation.
- Keep business logic in separate business services.
- Use bounded tool execution and iteration limits.
- Introduce LangGraph or MCP only when justified by future requirements.
