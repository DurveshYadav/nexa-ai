
from app.tools.v3.registry import ToolRegistry, ToolSpec

from app.tools.v3.schemas.orders import (
    GetOrderStatusInput,
    GetOrderDetailsInput,
    CancelOrderInput,
)
from app.tools.v3.schemas.products import (
    GetProductDetailsInput,
    CheckProductAvailabilityInput,
)
from app.tools.v3.schemas.customers import GetCustomerProfileInput
from app.tools.v3.schemas.support import CreateSupportTicketInput
from app.tools.v3.schemas.refunds import (
    CheckRefundEligibilityInput,
    RequestRefundInput,
    RefundData,
)


from app.tools.v3.handlers.orders import (
    get_order_status_handler,
    get_order_details_handler,
    cancel_order_handler,
)
from app.tools.v3.handlers.products import (
    get_product_details_handler,
    check_product_availability_handler,
)
from app.tools.v3.handlers.customers import get_customer_profile_handler
from app.tools.v3.handlers.support import create_support_ticket_handler
from app.tools.v3.handlers.refunds import (
    check_refund_eligibility_handler,
    request_refund_handler,
)


from app.tools.v3.schemas.results import (
    OrderStatusData,
    OrderDetailsData,
    CancelOrderData,
    ProductDetailsData,
    ProductAvailabilityData,
    CustomerProfileData,
    SupportTicketData,
)



def build_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    tools = [
        ToolSpec(
            name="get_order_status",
            description="Get the authenticated customer's order status.",
            input_schema=GetOrderStatusInput,
            handler=get_order_status_handler,
            permission="orders:read",
            service_dependencies=("order_service",),
        ),
        ToolSpec(
            name="get_order_details",
            description="Get the authenticated customer's order details.",
            input_schema=GetOrderDetailsInput,
            handler=get_order_details_handler,
            permission="orders:read",
            service_dependencies=("order_service",),
        ),
        ToolSpec(
            name="cancel_order",
            description="Cancel an eligible customer order.",
            input_schema=CancelOrderInput,
            handler=cancel_order_handler,
            permission="orders:write",
            service_dependencies=("order_service",),
        ),
        ToolSpec(
            name="get_product_details",
            description="Get product information and pricing.",
            input_schema=GetProductDetailsInput,
            handler=get_product_details_handler,
            permission="products:read",
            service_dependencies=("product_service",),
        ),
        ToolSpec(
            name="check_product_availability",
            description="Check available product quantity.",
            input_schema=CheckProductAvailabilityInput,
            handler=check_product_availability_handler,
            permission="products:read",
            service_dependencies=("product_service",),
        ),
        ToolSpec(
            name="get_customer_profile",
            description="Get the authenticated customer's profile.",
            input_schema=GetCustomerProfileInput,
            handler=get_customer_profile_handler,
            permission="customers:read",
            service_dependencies=("customer_service",),
        ),
        ToolSpec(
            name="create_support_ticket",
            description="Create a support ticket for the authenticated customer.",
            input_schema=CreateSupportTicketInput,
            handler=create_support_ticket_handler,
            permission="support:write",
            service_dependencies=("support_service",),
        ),
        ToolSpec(
            name="check_refund_eligibility",
            description="Check whether an order qualifies for a refund.",
            input_schema=CheckRefundEligibilityInput,
            handler=check_refund_eligibility_handler,
            permission="refunds:read",
            service_dependencies=("refund_service", "order_service"),
        ),
        ToolSpec(
            name="request_refund",
            description="Request a refund for an eligible order.",
            input_schema=RequestRefundInput,
            handler=request_refund_handler,
            permission="refunds:write",
            service_dependencies=("refund_service", "order_service"),
        ),
    ]

    for tool in tools:
        registry.register(tool)

    return registry

def get_llm_tool_definitions(registry: ToolRegistry) -> list[dict]:
    from app.tools.v3.definitions.tools import TOOL_DEFINITIONS

    definitions_by_name = {
        item["function"]["name"]: item
        for item in TOOL_DEFINITIONS
    }

    return [
        definitions_by_name[tool.name]
        for tool in registry.list_tools()
        if tool.enabled and tool.name in definitions_by_name
    ]
