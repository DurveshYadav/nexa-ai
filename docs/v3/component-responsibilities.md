# NexaAI V3 — Component Responsibilities

## 1. Agent API

Responsibilities:
- Expose POST /api/v3/agent/chat.
- Validate incoming requests.
- Authenticate users using existing V1 JWT dependencies.
- Pass requests to Agent Service.
- Return structured responses and HTTP errors.

Must not:
- Execute tools.
- Contain business logic.
- Access database repositories directly.
- Implement the LLM orchestration loop.

## 2. Agent Service

Responsibilities:
- Coordinate the agent use case.
- Verify conversation ownership.
- Load conversation history.
- Create execution context.
- Invoke Agent Orchestrator.
- Persist user and assistant messages.
- Return the final agent result.

Must not:
- Implement provider-specific API calls.
- Execute business operations directly.
- Trust user identity supplied by the LLM.

## 3. Agent Orchestrator

Responsibilities:
- Manage the LLM interaction loop.
- Send messages and available tools to LLM Provider.
- Detect tool-call requests.
- Delegate execution to Tool Executor.
- Send tool results back to the LLM.
- Stop after configured iteration or execution limits.
- Return the final assistant response.

Must not:
- Access database repositories.
- Bypass Tool Executor.
- Execute unregistered tools.
- Make authorization decisions independently.

## 4. LLM Provider

Responsibilities:
- Communicate with the configured LLM.
- Convert internal messages into provider requests.
- Normalize provider responses.
- Return text responses or structured tool calls.
- Handle provider errors and timeouts.

Must not:
- Execute business tools.
- Access user repositories.
- Make business authorization decisions.

## 5. Tool Registry

Responsibilities:
- Register approved tools.
- Store tool names and descriptions.
- Store argument schemas.
- Support tool lookup.
- Provide tool definitions to the LLM.

Must not:
- Execute tools.
- Access the database.
- Decide whether a user is authorized.

## 6. Tool Executor

Responsibilities:
- Find tools in Tool Registry.
- Validate tool arguments.
- Check permissions.
- Check approval requirements.
- Dispatch approved handlers.
- Normalize execution results.
- Handle execution errors.
- Record tool execution audit information.

Must not:
- Trust LLM-supplied identity.
- Execute unknown tools.
- Bypass approval requirements.
- Contain business rules.

## 7. Execution Context

Responsibilities:
- Carry trusted user_id.
- Carry conversation_id and run_id.
- Carry request_id.
- Carry permission information.
- Provide trusted execution metadata to tools.

Must not contain:
- Raw authentication tokens.
- API keys or passwords.
- Database sessions.
- Untrusted identity information from LLM arguments.

## 8. Tool Handlers

Responsibilities:
- Define the execution entry point for each tool.
- Validate tool-specific input.
- Delegate operations to Business Services.
- Return structured tool results.

Must not:
- Implement unrelated business logic.
- Access provider-specific LLM SDKs.
- Bypass authorization and approval checks.

## 9. Business Services

Responsibilities:
- Implement business operations.
- Apply business rules.
- Validate business conditions.
- Use repositories or external integrations.
- Return predictable results.

Must not:
- Depend on LLM provider SDKs.
- Parse natural-language prompts.
- Implement agent orchestration.

## 10. Repositories

Responsibilities:
- Read and write application data.
- Encapsulate database queries.
- Provide persistence operations to Business Services.

Must not:
- Call the LLM.
- Execute agent tool-selection logic.
- Interpret customer natural-language requests.

## 11. Component Communication

Agent API
  -> Agent Service
  -> Agent Orchestrator
  -> LLM Provider

Agent Orchestrator
  -> Tool Executor
  -> Tool Registry
  -> Tool Handler
  -> Business Service
  -> Repository
  -> Database

## 12. Key Design Principle

Each component has one clear responsibility.
Components communicate through defined interfaces.
Security checks happen in trusted backend layers.
Business logic remains independent of LLM orchestration.
