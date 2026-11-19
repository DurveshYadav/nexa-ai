from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Values can come from environment variables
    or the .env file.
    """

    # ---------------------------------------------------------
    # Application information
    # ---------------------------------------------------------

    app_name: str = "NexaAI"
    app_version: str = "1.0.0"
    debug: bool = True

    # ---------------------------------------------------------
    # API configuration
    # ---------------------------------------------------------

    api_v1_prefix: str = "/api/v1"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    # ---------------------------------------------------------
    # LLM configuration
    # ---------------------------------------------------------

    # Reads LLM_API_KEY from .env.
    #
    # Example:
    # LLM_API_KEY=your-api-key
    #
    # Do NOT put the real API key in Git.
    # llm_api_key: str
    openai_api_key: str
    openai_model: str = "gpt-5-mini"
    openai_timeout: int = 30

    chat_context_messages: int = 20

    # Database configuration
    database_url: str

    # ---------------------------------------------------------
    # Environment / .env configuration
    # ---------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Single configuration object used throughout the application.
settings = Settings()
