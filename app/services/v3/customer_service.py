class CustomerService:

    def __init__(self):
        self.customers = {
            1: {
                "customer_id": 1,
                "name": "Test Customer",
                "email": "customer@example.com",
                "phone": "9999999999",
            }
        }

    def get_customer_profile(self, customer_id: int) -> dict | None:
        return self.customers.get(customer_id)
