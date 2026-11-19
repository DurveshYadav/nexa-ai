from app.ai.schemas import AIMessage
from app.ai.service import ai_service


def main():
    response = ai_service.generate_response(
        [
            AIMessage(
                role="system",
                content="You are NexaAI, a concise assistant.",
            ),
            AIMessage(
                role="user",
                content="What is FastAPI?",
            ),
        ]
    )

    print("\n--- AI Response ---")
    print(response)

    print("\n--- Content ---")
    print(response.content)

    print("\n--- Model ---")
    print(response.model)

    print("\n--- Token Usage ---")
    print("Input:", response.input_tokens)
    print("Output:", response.output_tokens)


if __name__ == "__main__":
    main()
    