from app.ai.context import ContextBuilder
from app.models.message import Message


def test_context_builder_includes_system_prompt():

    builder = ContextBuilder()

    result = builder.build(
        history=[],
        current_message="Hello",
    )

    assert result[0].role == "system"
    assert result[-1].role == "user"
    assert result[-1].content == "Hello"

def test_context_builder_includes_history():

    builder = ContextBuilder()

    history = [
        Message(
            role="user",
            content="What is FastAPI?",
        ),
        Message(
            role="assistant",
            content="FastAPI is a Python framework.",
        ),
    ]

    result = builder.build(
        history=history,
        current_message="Why is it fast?",
    )

    assert result[0].role == "system"

    assert result[1].role == "user"
    assert result[1].content == "What is FastAPI?"

    assert result[2].role == "assistant"
    assert result[2].content == (
        "FastAPI is a Python framework."
    )

    assert result[3].role == "user"
    assert result[3].content == "Why is it fast?"

def test_context_is_chronological():

    builder = ContextBuilder()

    history = [
        Message(
            role="user",
            content="First",
        ),
        Message(
            role="assistant",
            content="Second",
        ),
    ]

    result = builder.build(
        history=history,
        current_message="Third",
    )

    contents = [
        message.content
        for message in result
    ]

    assert contents[-3:] == [
        "First",
        "Second",
        "Third",
    ]

def test_context_with_empty_history():

    builder = ContextBuilder()

    result = builder.build(
        history=[],
        current_message="Hello",
    )

    assert len(result) == 2

    assert result[0].role == "system"
    assert result[1].role == "user"

