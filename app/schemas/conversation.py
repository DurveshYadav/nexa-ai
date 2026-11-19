from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    """
    Request body for creating a conversation.
    """

    title: str = Field(
        min_length=1,
        max_length=100,
    )


class ConversationUpdate(BaseModel):
    """
    Request body for updating a conversation.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class ConversationResponse(BaseModel):
    """
    Public conversation response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    title: str
    created_at: datetime
    updated_at: datetime