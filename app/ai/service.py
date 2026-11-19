from app.ai.client import client
from app.ai.schemas import AIMessage, AIResponse
from app.core.config import settings
from openai import OpenAIError
# from app.core.exceptions import AIProviderTimeoutError, AIProviderError


class AIService:
    """
    Handles communication with the configured LLM.
    """

    def generate_response(
        self,
        messages: list[AIMessage],
    ) -> AIResponse:
        """
        Send messages to the LLM and return its response.
        """
        try:

            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in messages
                ],
            )
        
        except OpenAIError as exc:
            raise RuntimeError(
                "LLM provider request failed."
            ) from exc

        # except provider_timeout_exception:
        #     raise AIProviderTimeoutError()
        # except provider_exception:
        #     raise AIProviderError()

        content = response.choices[0].message.content or ""

        usage = response.usage

        return AIResponse(
            content=content,
            model=response.model,
            input_tokens=(
                usage.prompt_tokens
                if usage
                else None
            ),
            output_tokens=(
                usage.completion_tokens
                if usage
                else None
            ),
        )


ai_service = AIService()
