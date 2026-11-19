# NexaAI V3 — Support Workflows

## 1. Purpose

This document defines six customer-support workflows for the NexaAI V3 Support Agent.

The LLM interprets customer intent and proposes tool calls. The application validates, authorizes and executes them.

## 2. Common Agent Workflow

1. Customer sends a message.
2. API authenticates the customer using JWT.
3. Application identifies the authenticated user.
4. Agent receives the message and relevant conversation context.
5. LLM identifies the customer's intent.
6. LLM proposes a registered tool call.
7. Application validates the tool name and arguments.
8. Application checks authentication, ownership and permissions.
9. Tool executor invokes the business operation.
10. Tool result is returned to the agent.
11. Agent prepares a customer-friendly response.
12. Application records the execution outcome.

### Security Rules

- LLM must not execute database queries directly.
- LLM must not bypass the tool registry.
- Ownership must be checked by application logic.
- Tool failures must never be represented as success.
- Sensitive writes must follow the approved confirmation policy.

## 3. Workflow — Get Order Status

**Tool:** `get_order_status`

**Operation:** Read

### Customer Requests

- "Where is my order?"
- "Check my latest order."
- "Has order ORD-1001 been shipped?"

### Workflow

1. Customer asks an order-status question.
2. API authenticates the customer.
3. Agent identifies the intent as `get_order_status`.
4. Agent extracts the order identifier or asks for it.
5. Application validates the identifier.
6. Tool receives the authenticated user context and order identifier.
7. Business integration verifies order ownership.
8. Business system retrieves the order status.
9. Tool returns the result.
10. Agent explains the result to the customer.

### Example Input

```json
{
  "order_id": "ORD-1001"
}

## 5. Workflow — Get Customer Profile

**Tool:** `get_customer_profile`

**Operation:** Read

### Customer Requests

- "Show my profile."
- "Which email address is registered?"
- "What account information do you have about me?"

### Workflow

1. Customer requests their profile.
2. API authenticates the customer using JWT.
3. Agent identifies `get_customer_profile`.
4. Application obtains the authenticated user ID.
5. Tool retrieves only that user's permitted profile fields.
6. Tool returns the available profile information.
7. Agent presents the information.

### Example Input

```json
{}

