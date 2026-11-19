# NexaAI V3 — Architecture Decisions

## ADR-001: Controlled Tool-Using Agent

Status: Accepted

Decision:
Build a controlled AI agent that can request approved tools
to perform customer-support operations.

Reason:
The agent needs to interact with business systems without
giving the LLM unrestricted access.

## ADR-002: Custom Python Orchestration Loop

Status: Accepted

Decision:
Start with a custom Python orchestration loop.

Reason:
It provides direct control over tool execution, iteration
limits, error handling, and approval workflows.

Alternative:
LangGraph may be evaluated when workflows become more complex.

## ADR-003: Reuse Existing LLM Client

Status: Accepted

Decision:
Reuse the existing OpenAI client in app/ai/client.py through
a V3 provider adapter.

Reason:
Avoid duplicate clients and centralize existing configuration.

## ADR-004: Explicit Tool Registry

Status: Accepted

Decision:
Register approved tools explicitly using a Tool Registry.

Reason:
The LLM must not execute arbitrary functions or unregistered tools.

## ADR-005: Pydantic Tool Validation

Status: Accepted

Decision:
Use Pydantic schemas to validate tool arguments.

Reason:
Tool input must be validated before reaching business logic.

## ADR-006: Separate Business Services

Status: Accepted

Decision:
Keep business operations in dedicated Business Services.

Reason:
Business rules should remain independent of LLM orchestration
and provider-specific SDKs.

## ADR-007: Reuse Existing Database Layer

Status: Accepted

Decision:
Reuse existing NexaAI models and repositories where appropriate.

Reason:
Avoid duplicating database access and existing V1 functionality.

## ADR-008: Backend-Owned Execution Context

Status: Accepted

Decision:
Create trusted Execution Context in backend application code.

Reason:
LLM-supplied identity information must never determine
which customer's data can be accessed.

## ADR-009: Bounded Tool Execution

Status: Accepted

Decision:
Enforce maximum orchestration iterations, tool-call limits,
and appropriate timeouts.

Reason:
Prevent infinite loops and uncontrolled resource consumption.

## ADR-010: Approval for Sensitive Operations

Status: Accepted

Decision:
Require explicit approval for sensitive operations such as
order cancellation and refund requests.

Reason:
Sensitive business operations must not execute solely
because the LLM requested them.

## ADR-011: Defer MCP Integration

Status: Deferred

Decision:
Do not introduce MCP in the initial V3 implementation.

Reason:
Start with a simpler internal tool architecture.
Evaluate MCP when external tool interoperability becomes necessary.

## ADR-012: Defer Autonomous Agent Frameworks

Status: Deferred

Decision:
Do not introduce a complex autonomous-agent framework initially.

Reason:
The current support-agent use case can be implemented
with a controlled orchestration loop.

## Final Decision

Build NexaAI V3 incrementally using existing V1 infrastructure,
a reusable LLM provider adapter, explicit tool registration,
backend-controlled execution, and separate business services.
