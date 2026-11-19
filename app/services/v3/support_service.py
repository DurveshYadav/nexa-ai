class SupportService:

    def __init__(self):
        self.tickets = {}

    def create_ticket(
        self,
        customer_id: int,
        subject: str,
        description: str,
    ) -> dict:

        ticket_id = f"TKT-{len(self.tickets) + 1001}"

        ticket = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "subject": subject,
            "description": description,
            "status": "open",
        }

        self.tickets[ticket_id] = ticket
        return ticket
