from app.ai.prompts import DEFAULT_SYSTEM_PROMPT
from app.ai.schemas import AIMessage
from app.models.message import Message


class ContextBuilder:

    def build(
        self,
        history: list[Message],
        current_message: str,
    ) -> list[AIMessage]:

        messages = [
            AIMessage(
                role="system",
                # content=(
                #     "You are NexaAI, a helpful AI assistant. "
                #     "Be accurate, concise, and do not invent facts."
                # ),
                content=DEFAULT_SYSTEM_PROMPT,
            )
        ]

        for message in history:
            messages.append(
                AIMessage(
                    role=message.role,
                    content=message.content,
                )
            )

        messages.append(
            AIMessage(
                role="user",
                content=current_message,
            )
        )

        return messages


context_builder = ContextBuilder()



