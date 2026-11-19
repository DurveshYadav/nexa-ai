from app.tools.v3.context import ExecutionContext
from app.tools.v3.schemas.results import (
    CancelOrderData,
    OrderDetailsData,
    OrderStatusData,
    ToolError,
    ToolResult,
)
from app.services.v3.order_service import OrderService
from app.tools.v3.schemas.orders import (
    CancelOrderInput,
    GetOrderDetailsInput,
    GetOrderStatusInput,
)

def get_order_status_handler(
    arguments: GetOrderStatusInput,
    context: ExecutionContext,
    order_service: OrderService,
) -> ToolResult:

    order = order_service.get_order_status(
        order_id=arguments.order_id,
        customer_id=context.customer_id,
    )

    if order is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="ORDER_NOT_FOUND",
                message="Order not found.",
            ),
        )

    data = OrderStatusData(**order)

    return ToolResult(
        success=True,
        data=data.model_dump(),
    )

def get_order_details_handler(
    arguments: GetOrderDetailsInput,
    context: ExecutionContext,
    order_service: OrderService,
) -> ToolResult:

    order = order_service.get_order_details(
        order_id=arguments.order_id,
        customer_id=context.customer_id,
    )

    if order is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="ORDER_NOT_FOUND",
                message="Order not found.",
            ),
        )

    data = OrderDetailsData(**order)

    return ToolResult(
        success=True,
        data=data.model_dump(),
    )

def cancel_order_handler(
    arguments: CancelOrderInput,
    context: ExecutionContext,
    order_service: OrderService,
) -> ToolResult:

    order = order_service.cancel_order(
        order_id=arguments.order_id,
        customer_id=context.customer_id,
    )

    if order is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="ORDER_NOT_FOUND",
                message="Order not found.",
            ),
        )

    data = CancelOrderData(**order)

    if data.status != "cancelled":
        return ToolResult(
            success=False,
            data=data.model_dump(),
            error=ToolError(
                code="ORDER_CANNOT_BE_CANCELLED",
                message="Order cannot be cancelled.",
            ),
        )

    return ToolResult(
        success=True,
        data=data.model_dump(),
    )