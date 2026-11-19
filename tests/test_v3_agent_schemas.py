
import pytest
from pydantic import ValidationError

from app.api.v3.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
)


def test_valid_agent_chat_request():
    request = AgentChatRequest(message="Check my order")
    assert request.message == "Check my order"
    assert request.conversation_id is None


def test_invalid_agent_chat_request():
    with pytest.raises(ValidationError):
        AgentChatRequest(message="")


def test_agent_chat_response():
    response = AgentChatResponse(
        run_id="run-123",
        conversation_id=1,
        status="completed",
        message="Order shipped",
    )
    assert response.status == "completed"
