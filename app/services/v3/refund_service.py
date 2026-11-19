class RefundService:

    def __init__(self):
        self.refunds = {}

    def check_eligibility(
        self,
        order_id: str,
        customer_id: int,
        order_service,
    ) -> dict | None:

        order = order_service.get_order_details(order_id, customer_id)

        if order is None:
            return None

        eligible = order["status"] in ["delivered"]

        return {
            "order_id": order_id,
            "eligible": eligible,
            "status": order["status"],
            "message": (
                "Refund eligible."
                if eligible
                else "Order is not eligible for refund."
            ),
        }

    def request_refund(
        self,
        order_id: str,
        customer_id: int,
        order_service,
    ) -> dict | None:

        result = self.check_eligibility(
            order_id,
            customer_id,
            order_service,
        )

        if result is None or not result["eligible"]:
            return result

        if order_id in self.refunds:
            return {
                **result,
                "message": "Refund request already exists.",
            }

        self.refunds[order_id] = "requested"

        return {
            **result,
            "message": "Refund request submitted.",
        }

