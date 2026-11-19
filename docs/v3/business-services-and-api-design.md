# NexaAI V3 — Business Services & API Design

**Phase:** 5 of 18  
**Type:** Design + Architecture  
**Status:** Initial design

## 1. Objective

Define how the NexaAI Agent interacts with backend business operations
through secure, reusable business services.

The LLM may propose an operation. Backend services validate permissions,
apply business rules, and control all data changes.

## 2. Existing V1 Architecture to Reuse

V1 already provides:

- SQLAlchemy session management: `app/database/session.py`
- Authentication and database dependencies: `app/api/deps.py`
- User repository: `app/repositories/user_repository.py`
- Existing services and repositories.
- Application exceptions: `app/core/exceptions.py`
- Central exception handler: `app/core/exception_handlers.py`
- Request context and request ID middleware.

V3 must reuse these capabilities.

Do not create duplicate authentication, database session,
logging, or exception-handling systems.

## 3. Business Operation Flow

For an order status request:

1. Agent decides that order status is required.
2. Tool handler validates the tool arguments.
3. Handler obtains trusted customer identity from backend context.
4. OrderService applies ownership and business rules.
5. OrderRepository retrieves the order.
6. PostgreSQL returns the stored data.
7. Service returns a controlled result.
8. Agent uses that result to answer the customer.

The LLM must never directly access the database.

## 4. Layer Responsibilities

| Layer | Responsibility |
|---|---|
| API | HTTP, authentication, request validation |
| Tool Handler | Validate tool input and call business service |
| Business Service | Business rules, authorization, workflows |
| Repository | Database queries and persistence |
| Model | Database entity representation |
| Schema / DTO | Validated input and controlled output |

Business services must not depend on FastAPI Request or Response objects.

Repositories must not decide business policies.

Tool handlers must not contain business workflows.

## 5. Business Service Domains

### 5.1 OrderService

Responsibilities:

- Get order status.
- Get order details.
- Check cancellation eligibility.
- Cancel an eligible order.

Example methods:

- `get_order_status()`
- `get_order_details()`
- `check_cancellation_eligibility()`
- `cancel_order()`

### 5.2 ProductService

Responsibilities:

- Get product details.
- Check product availability.
- Get product price and description.

Example methods:

- `get_product()`
- `check_availability()`
- `get_product_price()`

### 5.3 CustomerService

Responsibilities:

- Get customer profile.
- Get permitted customer information.
- Update allowed profile fields.

Example methods:

- `get_customer_profile()`
- `get_customer_details()`
- `update_customer_profile()`

Apply privacy and ownership restrictions.

### 5.4 SupportService

Responsibilities:

- Create support tickets.
- Get ticket details.
- Update permitted ticket fields.
- Apply ticket priority rules.

Example methods:

- `create_ticket()`
- `get_ticket()`
- `update_ticket()`

### 5.5 RefundService

Responsibilities:

- Check refund eligibility.
- Submit refund requests.
- Get refund status.
- Prevent duplicate refund requests.

Example methods:

- `check_refund_eligibility()`
- `request_refund()`
- `get_refund_status()`

Refunds and order cancellations are separate business domains.


## 6. API, Service, Repository and Model Separation

- **API:** HTTP, authentication, request validation and responses.
- **Tool Handler:** validates tool arguments and invokes services.
- **Service:** business rules, ownership checks and workflows.
- **Repository:** database queries and persistence only.
- **Model:** database tables and relationships.
- **Schema / DTO:** validated input and controlled output.

Business services must not depend on FastAPI Request or Response.
Repositories must not contain business policies.
Tool handlers must not implement business workflows.


## 7. Business Rules

### 7.1 Order Cancellation

| Condition | Expected outcome |
|---|---|
| Order does not exist | Reject |
| Customer does not own order | Deny access |
| Order is delivered | Reject cancellation |
| Order is already cancelled | Return existing state |
| Order is eligible | Allow cancellation |
| Required approval is missing | Do not execute |

Eligibility checking and actual cancellation must be separate.

### 7.2 Refund

- Order must exist.
- Customer must own the order.
- Order must satisfy refund policy.
- Duplicate refund requests must be prevented.
- Refund status must come from backend data.
- Payment operations must follow provider rules.

### 7.3 Support Ticket

- Customer identity comes from authenticated context.
- Ticket creation requires valid input.
- Customers access only permitted tickets.
- Priority changes follow backend policy.
- Duplicate submissions must be handled safely.


## 8. Repository Design

| Repository | Responsibility |
|---|---|
| OrderRepository | Order database operations |
| ProductRepository | Product database operations |
| CustomerRepository | Customer database operations |
| SupportRepository | Support ticket database operations |
| RefundRepository | Refund database operations |

Repositories handle persistence only.

They must not decide cancellation eligibility, refund approval,
or customer permissions.


## 9. DTOs and Response Schemas

Use Pydantic schemas to validate input and control output.

- Define typed request and response models.
- Use `ConfigDict(extra="forbid")` to reject unexpected fields.
- Return only fields required by the caller.
- Never expose internal database fields unnecessarily.

Example response fields: `order_id`, `status`.

## 10. Database Transactions

- Multi-record operations must be atomic.
- Example: update order status and record an order event together.
- Commit only after all database operations succeed.
- Roll back if any database operation fails.
- Define transaction ownership at the service or Unit of Work level.
- V1 repositories currently commit independently; V3 workflows must avoid this pattern when multiple writes belong to one transaction.
- A PostgreSQL rollback cannot reverse an external payment already completed.
- Use idempotency, retries, outbox, saga, or compensation strategies where appropriate.

## 11. Idempotency

Idempotency prevents duplicate side effects when a request is retried.

Apply it to operations such as:
- Support ticket creation.
- Order cancellation.
- Refund requests.
- Payment operations.

Use a database uniqueness constraint scoped to the correct customer and operation. Make the check-and-create operation race-safe. Repeated requests with the same idempotency key should return the existing result instead of repeating the side effect.

## 12. Trusted Execution Context and Authorization

Define a backend-controlled execution context containing:

- `user_id`: authenticated application user.
- `customer_id`: trusted customer identity.
- `run_id`: agent execution identifier.
- `request_id`: HTTP request identifier.

The API authentication layer establishes identity. The tool handler passes trusted identity to the business service. Never trust an LLM-supplied customer ID for authorization. Every service must verify resource ownership before returning or changing customer data.

## 13. Error Handling

Use domain-specific errors such as:

- `OrderNotFoundError`
- `OrderAccessDeniedError`
- `OrderNotCancellableError`
- `RefundAlreadyRequestedError`

Separate domain errors from infrastructure errors. API endpoints map application errors to HTTP responses. Tool handlers convert expected errors into structured tool results. Never expose stack traces, secrets, SQL details, or internal provider errors to the LLM or customer.

## 14. Proposed V3 Package Structure

- `app/api/v3/endpoints/agent.py`
- `app/schemas/v3/`
- `app/services/v3/`
- `app/repositories/v3/`
- `app/tools/v3/handlers/`
- `app/models/`
- `app/core/`

Reuse V1 authentication, database sessions, logging, models, and exception conventions wherever appropriate. This is a proposed structure, not an instruction to create all files in Phase 5.

## 15. Testing Strategy

- Repository: existing and missing records.
- Service: ownership allowed and denied.
- OrderService: cancellation eligibility and rejection.
- RefundService: duplicate refund prevention.
- Tool handler: valid and invalid arguments.
- Transaction: commit and rollback behavior.

## 16. Phase 5 Completion Checklist

- [ ] API, service, repository, model and DTO responsibilities defined.
- [ ] Five business domains designed.
- [ ] Business rules and domain errors documented.
- [ ] Transaction ownership defined.
- [ ] Idempotency strategy documented.
- [ ] Trusted execution context and authorization defined.
- [ ] Agent-to-business-service flow documented.
- [ ] Testing strategy documented.
- [ ] Assignments completed.
- [ ] Quiz completed.

## 17. Phase 5 Assignments — Reference Answers

### A1. Business Service Responsibilities

- OrderService: get status, get details, check cancellation, cancel order.
- ProductService: get product, check availability, get price.
- CustomerService: get profile, get permitted details, update profile.
- SupportService: create ticket, get ticket, update ticket.
- RefundService: check eligibility, request refund, get refund status.

### A2. Layer Classification

| Operation | Layer |
|---|---|
| Fetch order by ID | Repository |
| Validate ownership | Business Service |
| Update order status | Repository, invoked by Service |
| Decide cancellation eligibility | Business Service |
| Store refund request | Repository, invoked by Service |
| Validate HTTP request | API / Schema |

### A3. Cancellation and Refund Rules

Cancellation:
1. Order missing: reject.
2. Customer is not owner: deny access.
3. Order delivered: reject cancellation.
4. Order already cancelled: return existing state.
5. Approval required but missing: do not execute.

Refund:
1. Order missing: reject.
2. Customer is not owner: deny access.
3. Order is outside refund policy: reject.
4. Refund already requested: return existing request.
5. Payment provider failure: report a controlled failure and retain retry/reconciliation information.

### A4. Example Tool Contracts

Get order status request: `{"order_id": 101}`

Get order status response: `{"order_id": 101, "status": "shipped"}`

Create support ticket request: `{"subject": "Delivery delay", "description": "Package has not arrived"}`

Create support ticket response: `{"ticket_id": 501, "status": "open"}`

Request refund request: `{"order_id": 101, "reason": "Damaged item", "idempotency_key": "refund-101-001"}`

Request refund response: `{"refund_id": 701, "status": "requested"}`

Customer identity is intentionally absent from these LLM-facing requests. Backend context supplies it.

### A5. Execution Flow

`Tool Handler -> Business Service -> Repository -> Database`

- Tool Handler: validates tool arguments and forwards trusted context.
- Business Service: checks ownership and business rules.
- Repository: performs database operations.
- Database: persists and retrieves records.

## 18. Phase 5 Quiz — Answer Key

1. Cancellation eligibility is decided by the Business Service.
2. Database queries belong to the Repository.
3. Authenticated customer identity comes from trusted backend execution context.
4. Idempotency prevents duplicate side effects after retries.
5. No. A PostgreSQL transaction cannot roll back an external payment that has already completed.

## 19. Phase 5 Completion

- [x] Architecture and layer separation documented.
- [x] Five business domains designed.
- [x] Business rules, errors, DTOs and transactions documented.
- [x] Idempotency and trusted authorization documented.
- [x] Testing strategy documented.
- [x] Assignments A1–A5 completed with reference answers.
- [x] Quiz answer key completed.
