
from dataclasses import dataclass, field

from app.services.v3.order_service import OrderService
from app.services.v3.product_service import ProductService
from app.services.v3.customer_service import CustomerService
from app.services.v3.support_service import SupportService
from app.services.v3.refund_service import RefundService


@dataclass
class ToolDependencies:
    order_service: OrderService = field(default_factory=OrderService)
    product_service: ProductService = field(default_factory=ProductService)
    customer_service: CustomerService = field(default_factory=CustomerService)
    support_service: SupportService = field(default_factory=SupportService)
    refund_service: RefundService = field(default_factory=RefundService)

