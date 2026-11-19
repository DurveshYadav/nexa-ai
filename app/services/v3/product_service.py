class ProductService:

    def __init__(self):
        self.products = {
            "PROD-101": {
                "product_id": "PROD-101",
                "product_name": "Wireless Headphones",
                "description": "Bluetooth headphones",
                "price": 2499.00,
                "available_quantity": 10,
            },
            "PROD-102": {
                "product_id": "PROD-102",
                "product_name": "Wireless Mouse",
                "description": "Wireless optical mouse",
                "price": 999.00,
                "available_quantity": 25,
            },
        }

    def get_product_details(
        self,
        product_id: str,
    ) -> dict | None:
        return self.products.get(product_id)

    def check_product_availability(
        self,
        product_id: str,
    ) -> dict | None:
        product = self.products.get(product_id)

        if product is None:
            return None

        return {
            "product_id": product["product_id"],
            "available": product["available_quantity"] > 0,
            "available_quantity": product["available_quantity"],
        }

