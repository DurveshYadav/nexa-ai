from app.services.v3.order_service import OrderService
from app.services.v3.refund_service import RefundService
from app.tools.v3.context import ExecutionContext
from app.tools.v3.schemas.refunds import (
    CheckRefundEligibilityInput,
    RequestRefundInput,
    RefundData,
)
from app.tools.v3.schemas.results import ToolError, ToolResult


def check_refund_eligibility_handler(
    arguments: CheckRefundEligibilityInput,
    context: ExecutionContext,
    refund_service: RefundService,
    order_service: OrderService,
) -> ToolResult:

    result = refund_service.check_eligibility(
        arguments.order_id,
        context.customer_id,
        order_service,
    )

    if result is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="ORDER_NOT_FOUND",
                message="Order not found.",
            ),
        )

    data = RefundData(**result)

    return ToolResult(
        success=data.eligible,
        data=data.model_dump(),
        error=None if data.eligible else ToolError(
            code="REFUND_NOT_ELIGIBLE",
            message=data.message,
        ),
    )


def request_refund_handler(
    arguments: RequestRefundInput,
    context: ExecutionContext,
    refund_service: RefundService,
    order_service: OrderService,
) -> ToolResult:

    result = refund_service.request_refund(
        arguments.order_id,
        context.customer_id,
        order_service,
    )

    if result is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="ORDER_NOT_FOUND",
                message="Order not found.",
            ),
        )

    data = RefundData(**result)

    return ToolResult(
        success=data.eligible,
        data=data.model_dump(),
        error=None if data.eligible else ToolError(
            code="REFUND_NOT_ELIGIBLE",
            message=data.message,
        ),
    )


