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
)


def build_tool_definition(name: str, description: str, schema) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": schema.model_json_schema(),
        },
    }


TOOL_DEFINITIONS = [
    build_tool_definition("get_order_status", "Get order status.", GetOrderStatusInput),
    build_tool_definition("get_order_details", "Get order details.", GetOrderDetailsInput),
    build_tool_definition("cancel_order", "Cancel an eligible order.", CancelOrderInput),
    build_tool_definition("get_product_details", "Get product details.", GetProductDetailsInput),
    build_tool_definition("check_product_availability", "Check product stock.", CheckProductAvailabilityInput),
    build_tool_definition("get_customer_profile", "Get the authenticated customer's profile.", GetCustomerProfileInput),
    build_tool_definition("create_support_ticket", "Create a customer support ticket.", CreateSupportTicketInput),
    build_tool_definition("check_refund_eligibility", "Check refund eligibility.", CheckRefundEligibilityInput),
    build_tool_definition("request_refund", "Submit a refund request.", RequestRefundInput),
]

