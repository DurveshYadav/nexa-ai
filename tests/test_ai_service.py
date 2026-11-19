
from unittest.mock import patch

import pytest
from openai import OpenAIError

from app.ai.schemas import AIMessage
from app.ai.service import ai_service


def test_generate_response():
    messages = [
        AIMessage(
            role="system",
            content="You are NexaAI.",
        ),
        AIMessage(
            role="user",
            content="What is FastAPI?",
        ),
    ]

    fake_response = {
        "content": "FastAPI is a Python web framework.",
        "model": "test-model",
        "input_tokens": 10,
        "output_tokens": 8,
    }

    with patch(
        "app.ai.service.client.chat.completions.create"
    ) as mock_create:

        mock_create.return_value.choices = [
            type(
                "Choice",
                (),
                {
                    "message": type(
                        "Message",
                        (),
                        {
                            "content": fake_response["content"]
                        },
                    )()
                },
            )()
        ]

        mock_create.return_value.model = fake_response["model"]

        mock_create.return_value.usage = type(
            "Usage",
            (),
            {
                "prompt_tokens": fake_response["input_tokens"],
                "completion_tokens": fake_response["output_tokens"],
            },
        )()

        response = ai_service.generate_response(messages)

    assert response.content == (
        "FastAPI is a Python web framework."
    )
    assert response.model == "test-model"
    assert response.input_tokens == 10
    assert response.output_tokens == 8

    mock_create.assert_called_once()


def test_generate_response_openai_error():
    """
    Verify OpenAI errors are converted to RuntimeError.
    """

    messages = [
        AIMessage(
            role="user",
            content="Hello",
        ),
    ]

    with patch(
        "app.ai.service.client.chat.completions.create"
    ) as mock_create:

        mock_create.side_effect = OpenAIError(
            "Provider failed"
        )

        with pytest.raises(
            RuntimeError,
            match="LLM provider request failed.",
        ):
            ai_service.generate_response(messages)

# from unittest.mock import patch

# from app.ai.schemas import AIMessage
# from app.ai.service import ai_service


# def test_generate_response():
#     messages = [
#         AIMessage(
#             role="system",
#             content="You are NexaAI.",
#         ),
#         AIMessage(
#             role="user",
#             content="What is FastAPI?",
#         ),
#     ]

#     fake_response = {
#         "content": "FastAPI is a Python web framework.",
#         "model": "test-model",
#         "input_tokens": 10,
#         "output_tokens": 8,
#     }

#     with patch(
#         "app.ai.service.client.chat.completions.create"
#     ) as mock_create:

#         # Mock OpenAI response
#         mock_create.return_value.choices = [
#             type(
#                 "Choice",
#                 (),
#                 {
#                     "message": type(
#                         "Message",
#                         (),
#                         {
#                             "content": fake_response["content"]
#                         },
#                     )()
#                 },
#             )()
#         ]

#         mock_create.return_value.model = fake_response["model"]

#         mock_create.return_value.usage = type(
#             "Usage",
#             (),
#             {
#                 "prompt_tokens": fake_response["input_tokens"],
#                 "completion_tokens": fake_response["output_tokens"],
#             },
#         )()

#         response = ai_service.generate_response(messages)

#     assert response.content == (
#         "FastAPI is a Python web framework."
#     )

#     assert response.model == "test-model"

#     assert response.input_tokens == 10

#     assert response.output_tokens == 8

#     mock_create.assert_called_once()

