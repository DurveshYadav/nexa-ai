from sqlalchemy.orm import Session
from app.core.config import settings
from app.ai.context import context_builder
# from app.ai.schemas import AIMessage
from app.ai.service import ai_service
from app.models.conversation import Conversation
from app.repositories.message_repository import MessageRepository


class ChatService:

    def __init__(self):
        self.message_repository = MessageRepository()

    def send_message(
        self,
        db: Session,
        conversation: Conversation,
        content: str,
    ):

        # 1. Load recent conversation history.
        history = self.message_repository.get_recent(
            db=db,
            conversation_id=conversation.id,
            # limit=20,
            limit=settings.chat_context_messages,
        )

        # # 1. Save user message.
        # user_message = self.message_repository.create(
        #     db=db,
        #     conversation_id=conversation.id,
        #     role="user",
        #     content=content,
        # )

        # # 2. Build messages for the LLM.
        # ai_messages = [
        #     AIMessage(
        #         role="system",
        #         content="You are NexaAI, a helpful AI assistant.",
        #     ),
        #     AIMessage(
        #         role="user",
        #         content=content,
        #     ),
        # ]

        # 2. Build LLM context.
        ai_messages = context_builder.build(
            history=history,
            current_message=content,
        )

        # 3. Call LLM.
        ai_response = ai_service.generate_response(
            ai_messages
        )

        # 4. Save current user message.
        user_message = self.message_repository.create(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content=content,
        )

        # # 4. Save assistant response.
        # assistant_message = self.message_repository.create(
        #     db=db,
        #     conversation_id=conversation.id,
        #     role="assistant",
        #     content=ai_response.content,
        #     model=ai_response.model,
        #     input_tokens=ai_response.input_tokens,
        #     output_tokens=ai_response.output_tokens,
        # )

        # # 5. Return everything needed by API.
        # return {
        #     "user_message": user_message,
        #     "assistant_message": assistant_message,
        #     "model": ai_response.model,
        #     "input_tokens": ai_response.input_tokens,
        #     "output_tokens": ai_response.output_tokens,
        # }

        # 5. Save assistant response.
        assistant_message = self.message_repository.create(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response.content,
            model=ai_response.model,
            input_tokens=ai_response.input_tokens,
            output_tokens=ai_response.output_tokens,
        )

        # 6. Return API response.
        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "model": ai_response.model,
            "input_tokens": ai_response.input_tokens,
            "output_tokens": ai_response.output_tokens,
        }


chat_service = ChatService()
