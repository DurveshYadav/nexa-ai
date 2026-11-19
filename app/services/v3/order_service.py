class OrderService:

    def __init__(self):
        self.orders = {
            "ORD-10025": {
                "order_id": "ORD-10025",
                "customer_id": 1,
                "status": "shipped",
                "tracking_number": "TRK-50025",
                "total_amount": 2499.00,
                "items": [
                    {
                        "product_id": "PROD-101",
                        "product_name": "Wireless Headphones",
                        "quantity": 1,
                    }
                ],
            },
            "ORD-10026": {
                "order_id": "ORD-10026",
                "customer_id": 1,
                "status": "pending",
                "tracking_number": None,
                "total_amount": 999.00,
                "items": [
                    {
                        "product_id": "PROD-102",
                        "product_name": "Wireless Mouse",
                        "quantity": 1,
                    }
                ],
            },
        }

    def _get_customer_order(
        self,
        order_id: str,
        customer_id: int,
    ) -> dict | None:

        order = self.orders.get(order_id)

        if order is None or order["customer_id"] != customer_id:
            return None

        return order

    def get_order_status(
        self,
        order_id: str,
        customer_id: int,
    ) -> dict | None:
        order = self._get_customer_order(order_id, customer_id)

        if order is None:
            return None

        return {
            "order_id": order["order_id"],
            "status": order["status"],
            "tracking_number": order["tracking_number"],
        }

    def get_order_details(
        self,
        order_id: str,
        customer_id: int,
    ) -> dict | None:
        order = self._get_customer_order(order_id, customer_id)

        if order is None:
            return None

        return {
            key: value
            for key, value in order.items()
            if key != "customer_id"
        }

    def cancel_order(
        self,
        order_id: str,
        customer_id: int,
    ) -> dict | None:
        order = self._get_customer_order(order_id, customer_id)

        if order is None:
            return None

        if order["status"] not in ["pending", "processing"]:
            return {
                "order_id": order_id,
                "status": order["status"],
                "message": "Order cannot be cancelled.",
            }

        order["status"] = "cancelled"

        return {
            "order_id": order_id,
            "status": "cancelled",
            "message": "Order cancelled successfully.",
        }

