# NexaAI V3 — Agent Execution Flow

## 1. Objective

Define the complete lifecycle of a customer request handled by
the NexaAI Support Agent.

## 2. Normal Request Flow

1. Client sends a customer message.
2. Agent API receives POST /api/v3/agent/chat.
3. API validates the request.
4. Existing V1 authentication identifies the current user.
5. Agent Service verifies conversation ownership.
6. Agent Service loads conversation history.
7. Agent Service creates trusted Execution Context.
8. Agent Service invokes Agent Orchestrator.
9. Orchestrator sends conversation context and approved tool
   definitions to LLM Provider.
10. LLM Provider returns either a normal response or tool calls.
11. If there are no tool calls, Orchestrator returns the response.
12. If tool calls exist, Orchestrator delegates them to Tool Executor.
13. Tool Executor validates arguments and checks permissions.
14. Approved Tool Handler calls the relevant Business Service.
15. Business Service performs the operation using repositories
    or external integrations.
16. Tool Executor returns a normalized result.
17. Orchestrator sends the tool result back to the LLM.
18. The LLM produces the final response.
19. Agent Service persists the conversation messages.
20. Agent API returns the response to the client.

## 3. Tool Execution Flow

LLM Tool Call
  |
  v
Tool Executor
  |
  v
Tool Registry Lookup
  |
  v
Argument Validation
  |
  v
Permission Check
  |
  v
Approval Check
  |
  v
Tool Handler
  |
  v
Business Service
  |
  v
Repository / External API
  |
  v
Normalized Tool Result
  |
  v
Agent Orchestrator

## 4. Sensitive Operation Flow

For operations such as cancellation or refund:

1. LLM requests the sensitive operation.
2. Tool Executor validates the requested operation.
3. Backend checks user permissions and resource ownership.
4. Approval Service determines whether confirmation is required.
5. If approval is required, execution pauses.
6. Agent asks the customer for confirmation.
7. Backend receives and validates the confirmation.
8. Authorization and business conditions are checked again.
9. The operation executes only after approval.
10. The result is recorded and returned to the agent.

The LLM cannot approve an operation on behalf of the customer.

## 5. Error Flow

- Invalid request: API returns a validation error.
- Invalid authentication: API returns an authentication error.
- Conversation not owned by user: request is rejected.
- Unknown tool: Tool Executor rejects execution.
- Invalid arguments: validation error is returned.
- Permission denied: execution is rejected.
- Approval pending: operation remains unexecuted.
- Tool failure: structured failure is returned to Orchestrator.
- LLM failure or timeout: Agent Service handles the failure.
- Unexpected failure: error is logged and safely reported.

Never return a successful business-operation message when
the operation has failed.

## 6. Execution Limits

The Orchestrator must enforce:
- Maximum orchestration iterations.
- Maximum tool calls per run.
- Provider timeout.
- Tool execution timeout where supported.
- Controlled handling of repeated tool calls.

## 7. Final Response

The final API response should communicate:
- Agent response text.
- Conversation identifier.
- Run identifier when available.
- Execution status.
- Relevant tool execution information where appropriate.

Do not expose secrets, internal credentials, or sensitive
backend implementation details.

## 8. Key Principle

The LLM decides what it wants to request.
The backend decides what is permitted.
Business Services decide whether the operation is valid.
Only the backend executes the actual operation.
