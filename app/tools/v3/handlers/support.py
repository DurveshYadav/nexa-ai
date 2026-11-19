from app.services.v3.support_service import SupportService
from app.tools.v3.context import ExecutionContext
from app.tools.v3.schemas.support import CreateSupportTicketInput
from app.tools.v3.schemas.results import (
    SupportTicketData,
    ToolResult,
)


def create_support_ticket_handler(
    arguments: CreateSupportTicketInput,
    context: ExecutionContext,
    support_service: SupportService,
) -> ToolResult:

    ticket = support_service.create_ticket(
        customer_id=context.customer_id,
        subject=arguments.subject,
        description=arguments.description,
    )

    data = SupportTicketData(**ticket)

    return ToolResult(
        success=True,
        data=data.model_dump(),
    )


