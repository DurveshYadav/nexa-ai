import pytest
from types import SimpleNamespace
from app.integrations.llm.openai_provider import OpenAIProvider

def test_openai_provider_normal_response(monkeypatch):
    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="Hello! How can I help?",
                    tool_calls=None,
                ),
                finish_reason="stop",
            )
        ],
        model="gpt-5-mini",
        usage=SimpleNamespace(
            prompt_tokens=10,
            completion_tokens=8,
        ),
    )

    def mock_create(**kwargs):
        return mock_response

    monkeypatch.setattr(
        "app.integrations.llm.openai_provider.client.chat.completions.create",
        mock_create,
    )

    provider = OpenAIProvider()
    response = provider.generate(
        messages=[{"role": "user", "content": "Hello"}]
    )

    assert response.content == "Hello! How can I help?"
    assert response.tool_calls == []
    assert response.model == "gpt-5-mini"
    assert response.input_tokens == 10
    assert response.output_tokens == 8
    assert response.finish_reason == "stop"

def test_openai_provider_tool_call_response(monkeypatch):
    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[
                        SimpleNamespace(
                            id="call_123",
                            function=SimpleNamespace(
                                name="get_order_status",
                                arguments='{"order_id": "ORD-10025"}',
                            ),
                        )
                    ],
                ),
                finish_reason="tool_calls",
            )
        ],
        model="gpt-5-mini",
        usage=SimpleNamespace(
            prompt_tokens=20,
            completion_tokens=12,
        ),
    )

    def mock_create(**kwargs):
        assert "tools" in kwargs
        assert kwargs["tool_choice"] == "auto"
        return mock_response

    monkeypatch.setattr(
        "app.integrations.llm.openai_provider.client.chat.completions.create",
        mock_create,
    )

    provider = OpenAIProvider()

    response = provider.generate(
        messages=[{"role": "user", "content": "Check my order"}],
        tools=[
            {
                "type": "function",
                "function": {"name": "get_order_status"},
            }
        ],
    )

    assert response.content is None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].id == "call_123"
    assert response.tool_calls[0].name == "get_order_status"
    assert response.tool_calls[0].arguments == {
        "order_id": "ORD-10025"
    }
    assert response.finish_reason == "tool_calls"

def test_openai_provider_rejects_empty_choices(monkeypatch):
        mock_response = SimpleNamespace(choices=[])

        monkeypatch.setattr(
            "app.integrations.llm.openai_provider.client.chat.completions.create",
            lambda **kwargs: mock_response,
        )

        provider = OpenAIProvider()

        with pytest.raises(
            ValueError,
            match="LLM returned no response choices",
        ):
            provider.generate(
                messages=[{"role": "user", "content": "Hello"}]
            )

def test_openai_provider_rejects_malformed_tool_arguments(monkeypatch):
        mock_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=None,
                        tool_calls=[
                            SimpleNamespace(
                                id="call_invalid",
                                function=SimpleNamespace(
                                    name="get_order_status",
                                    arguments='{"order_id": ',
                                ),
                            )
                        ],
                    ),
                    finish_reason="tool_calls",
                )
            ],
            model="test-model",
            usage=None,
        )

        monkeypatch.setattr(
            "app.integrations.llm.openai_provider.client.chat.completions.create",
            lambda **kwargs: mock_response,
        )

        provider = OpenAIProvider()

        with pytest.raises(ValueError):
            provider.generate(
                messages=[{"role": "user", "content": "Check order"}]
            )


def test_openai_provider_rejects_non_object_tool_arguments(monkeypatch):
        mock_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=None,
                        tool_calls=[
                            SimpleNamespace(
                                id="call_list",
                                function=SimpleNamespace(
                                    name="get_order_status",
                                    arguments='["ORD-10025"]',
                                ),
                            )
                        ],
                    ),
                    finish_reason="tool_calls",
                )
            ],
            model="test-model",
            usage=None,
        )

        monkeypatch.setattr(
            "app.integrations.llm.openai_provider.client.chat.completions.create",
            lambda **kwargs: mock_response,
        )

        provider = OpenAIProvider()

        with pytest.raises(
            ValueError,
            match="Tool arguments must be a JSON object",
        ):
            provider.generate(
                messages=[{"role": "user", "content": "Check order"}]
            )
