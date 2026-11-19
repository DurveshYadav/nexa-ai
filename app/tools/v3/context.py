
from dataclasses import dataclass, field

from sqlalchemy.orm import Session


@dataclass(frozen=True)
class ExecutionContext:
    user_id: int
    customer_id: int
    run_id: str
    request_id: str
    permissions: frozenset[str] = field(default_factory=frozenset)
    conversation_id: int | None = None
    db: Session | None = field(default=None, repr=False, compare=False)
