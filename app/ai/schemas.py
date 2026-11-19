from pydantic import BaseModel


class AIMessage(BaseModel):
    role: str
    content: str


class AIResponse(BaseModel):
    content: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    
    