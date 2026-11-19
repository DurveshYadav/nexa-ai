# NexaAI V3 — Business Requirements

## 1. Overview

NexaAI V3 introduces a Support Agent that understands customer support requests and selects appropriate business tools to answer them.

The agent will use controlled tool execution rather than relying only on an LLM-generated response.

## 2. Business Problem

Customers need a single conversational interface to:
- Check their order status.
- Retrieve product information.
- View their own customer profile.
- Create support tickets.
- Request order cancellation.
- Request refunds.

Currently, NexaAI V1 provides conversational AI capabilities and V2 provides ML prediction capabilities. Neither version provides controlled business-support operations.

V3 bridges this gap through an LLM-powered Support Agent and a defined set of business tools.

## 3. Goals

1. Understand customer support requests expressed in natural language.
2. Identify the appropriate business operation.
3. Select an approved tool for the requested operation.
4. Validate tool inputs before execution.
5. Restrict customer data access to the authenticated user.
6. Handle sensitive operations with explicit authorization and confirmation.
7. Return understandable responses and useful error messages.
8. Maintain traceability of agent and tool execution.

## 4. Out of Scope

The following are not part of V3's initial scope:

- Retrieval-Augmented Generation (RAG) and document knowledge bases — V4.
- Fully autonomous multi-step business processes — V5.
- Unrestricted database access by the LLM.
- LLM-generated SQL execution.
- Unauthenticated business operations.
- Real payment processing or refund settlement without an approved business integration.
- MCP and advanced LangGraph orchestration as mandatory dependencies.

## 5. Actors

| Actor | Responsibility |
|---|---|
| Customer | Requests support using natural language |
| Support Agent | Understands requests and coordinates tools |
| LLM | Interprets intent and proposes tool calls |
| Tool Executor | Validates and executes approved tools |
| Business System | Provides order, product, ticket and refund data |
| Authenticated User | Provides verified identity through JWT |
| Administrator/Support Staff | Handles operations requiring staff authorization |

## 6. Existing NexaAI Capabilities

V3 must preserve and reuse existing capabilities:

- V1 JWT authentication.
- Existing User model and authenticated user dependency.
- Existing Conversation and Message models.
- Existing PostgreSQL and SQLAlchemy configuration.
- Existing request ID and logging infrastructure.
- Existing V1 and V2 API behavior.

Existing models must not be duplicated.

## 7. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Accept customer support messages |
| FR-02 | Identify the customer's intent |
| FR-03 | Select an appropriate registered tool |
| FR-04 | Validate tool arguments |
| FR-05 | Retrieve order status |
| FR-06 | Retrieve product details |
| FR-07 | Retrieve the authenticated customer's available profile |
| FR-08 | Create a support ticket |
| FR-09 | Process an authorized cancellation request |
| FR-10 | Process an authorized refund request |
| FR-11 | Enforce customer ownership checks |
| FR-12 | Require confirmation for sensitive operations according to policy |
| FR-13 | Return clear success and failure responses |
| FR-14 | Record execution outcomes for traceability |

## 8. Non-Functional Requirements

- Security: JWT authentication and ownership validation.
- Authorization: tools must enforce operation-specific permissions.
- Reliability: tool failures must not be presented as successful operations.
- Observability: execution should be traceable using request and run identifiers.
- Maintainability: tools must have clear schemas and isolated responsibilities.
- Testability: business logic and tool execution must be independently testable.
- Compatibility: existing V1 and V2 APIs must continue working.

## 9. Initial Tool Scope

| Tool | Operation | Initial classification |
|---|---|---|
| get_order_status | Read order information | Read |
| get_product_details | Read product information | Read |
| get_customer_profile | Read own profile | Read |
| create_support_ticket | Create support request | Controlled write |
| cancel_order | Cancel an order | Sensitive write |
| request_refund | Request a refund | Sensitive write |

These tools are logical capabilities. Their actual business-system integrations and data sources must be defined before implementation.

## 10. Identity and Data Ownership

- Every customer-facing operation must use the authenticated user context.
- The agent must never accept a customer identity supplied in natural language as proof of ownership.
- A customer may access only records they are authorized to access.
- Tool implementations must enforce ownership independently of LLM instructions.
- The existing User model currently exposes only ID, email, password hash and timestamps.
- Additional profile fields require a separately reviewed data-model decision.

## 11. Sensitive Operations

Order cancellation and refund requests are sensitive operations.

Before implementation, the business policy must define:
- Eligibility conditions.
- Required confirmation.
- Authorization requirements.
- Duplicate-request handling.
- Failure and rollback behavior.
- Whether staff approval is required.

The LLM must never approve its own proposed operation.

## 12. V3 Success Criteria

V3 is successful when:
- The agent can identify the six defined support intents.
- Tool calls are validated and executed through a controlled executor.
- Customer ownership is enforced.
- Sensitive operations follow explicit business policies.
- Tool failures are handled safely.
- Existing V1 and V2 functionality remains unaffected.

## 13. Dependencies and Assumptions

The initial repository does not currently contain order, product, or support-ticket models.

Therefore, these capabilities require either:
1. Integration with an existing external business system; or
2. A separately designed and approved internal business-data implementation.

No assumption is made that these systems or datasets already exist.
