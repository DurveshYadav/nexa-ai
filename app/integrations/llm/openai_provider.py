import json
import logging
from typing import Any

import time
from app.ai.client import client
from app.core.config import settings
from app.integrations.llm.base import BaseLLMProvider
from app.integrations.llm.schemas import LLMResponse, LLMToolCall


logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):

    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> LLMResponse:

        request_data = {
            "model": settings.openai_model,
            "messages": messages,
        }

        if tools:
            request_data["tools"] = tools
            request_data["tool_choice"] = "auto"

        started_at = time.perf_counter()
        response = client.chat.completions.create(
            **request_data,
            timeout=settings.openai_timeout,
        )
        duration_ms = (time.perf_counter() - started_at) * 1000

        if not response.choices:
            raise ValueError("LLM returned no response choices.")

        message = response.choices[0].message
        tool_calls = []

        for tool_call in message.tool_calls or []:
            arguments = json.loads(tool_call.function.arguments)

            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments must be a JSON object.")

            tool_calls.append(
                LLMToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=arguments,
                )
            )

        usage = response.usage
        logger.info(
            "llm_request_completed model=%s duration_ms=%.2f "
            "input_tokens=%s output_tokens=%s finish_reason=%s",
            response.model,
            duration_ms,
            usage.prompt_tokens if usage else None,
            usage.completion_tokens if usage else None,
            response.choices[0].finish_reason,
        )
        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            model=response.model,
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
            finish_reason=response.choices[0].finish_reason,
        )

