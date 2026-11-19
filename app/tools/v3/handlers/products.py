from app.services.v3.product_service import ProductService
from app.tools.v3.context import ExecutionContext
from app.tools.v3.schemas.products import (
    CheckProductAvailabilityInput,
    GetProductDetailsInput,
)
from app.tools.v3.schemas.results import (
    ProductAvailabilityData,
    ProductDetailsData,
    ToolError,
    ToolResult,
)



def get_product_details_handler(
    arguments: GetProductDetailsInput,
    context: ExecutionContext,
    product_service: ProductService,
) -> ToolResult:

    product = product_service.get_product_details(
        product_id=arguments.product_id,
    )

    if product is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="PRODUCT_NOT_FOUND",
                message="Product not found.",
            ),
        )

    data = ProductDetailsData(**product)

    return ToolResult(
        success=True,
        data=data.model_dump(),
    )

def check_product_availability_handler(
    arguments: CheckProductAvailabilityInput,
    context: ExecutionContext,
    product_service: ProductService,
) -> ToolResult:

    availability = product_service.check_product_availability(
        product_id=arguments.product_id,
    )

    if availability is None:
        return ToolResult(
            success=False,
            error=ToolError(
                code="PRODUCT_NOT_FOUND",
                message="Product not found.",
            ),
        )

    data = ProductAvailabilityData(**availability)

    return ToolResult(
        success=True,
        data=data.model_dump(),
    )