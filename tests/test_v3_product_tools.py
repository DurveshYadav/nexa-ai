from app.services.v3.product_service import ProductService
from app.tools.v3.context import ExecutionContext
from app.tools.v3.handlers.products import get_product_details_handler
from app.tools.v3.schemas.products import GetProductDetailsInput
from app.tools.v3.handlers.products import check_product_availability_handler
from app.tools.v3.schemas.products import CheckProductAvailabilityInput


def test_get_product_details_success():
    result = get_product_details_handler(
        GetProductDetailsInput(product_id="PROD-101"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        ProductService(),
    )

    assert result.success is True
    assert result.data["product_id"] == "PROD-101"
    assert result.data["product_name"] == "Wireless Headphones"


def test_get_product_details_not_found():
    result = get_product_details_handler(
        GetProductDetailsInput(product_id="PROD-999"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        ProductService(),
    )

    assert result.success is False
    assert result.error.code == "PRODUCT_NOT_FOUND"

def test_check_product_availability_success():
    result = check_product_availability_handler(
        CheckProductAvailabilityInput(product_id="PROD-101"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        ProductService(),
    )

    assert result.success is True
    assert result.data["available"] is True
    assert result.data["available_quantity"] == 10


def test_check_product_availability_not_found():
    result = check_product_availability_handler(
        CheckProductAvailabilityInput(product_id="PROD-999"),
        ExecutionContext(1, 1, "run-1", "req-1"),
        ProductService(),
    )

    assert result.success is False
    assert result.error.code == "PRODUCT_NOT_FOUND"
