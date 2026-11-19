from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=10000,
    )


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime


class ChatResponse(BaseModel):
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse

    model: str

    input_tokens: int | None = None
    output_tokens: int | None = None

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    created_at: datetime

class MessageHistoryResponse(BaseModel):
    items: list[MessageResponse]
    skip: int
    limit: int
    