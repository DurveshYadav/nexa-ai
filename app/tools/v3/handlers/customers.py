
from app.services.v3.customer_service import CustomerService
from app.tools.v3.context import ExecutionContext
from app.tools.v3.schemas.customers import GetCustomerProfileInput
from app.tools.v3.schemas.results import (
    CustomerProfileData,
    ToolError,
    ToolResult,
)


def get_customer_profile_handler(
    context: ExecutionContext,
    customer_service: CustomerService,
    arguments: GetCustomerProfileInput | None = None,
) -> ToolResult:

    customer = customer_service.get_customer_profile(
        customer_id=context.customer_id,
    )

    if customer is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="CUSTOMER_NOT_FOUND",
                message="Customer not found.",
            ),
        )

    data = CustomerProfileData(**customer)

    return ToolResult(
        success=True,
        data=data.model_dump(),
    )
