class NexaAIException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        code: str = "NEXAAI_ERROR",
    ):
        self.message = message
        self.code = code

        super().__init__(message)


class ResourceNotFoundError(NexaAIException):
    def __init__(
        self,
        message: str = "Resource not found.",
    ):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
        )


class AuthenticationError(NexaAIException):
    def __init__(
        self,
        message: str = "Authentication failed.",
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(NexaAIException):
    def __init__(
        self,
        message: str = "You are not authorized to access this resource.",
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
        )


class AIProviderError(NexaAIException):
    def __init__(
        self,
        message: str = "AI provider request failed.",
    ):
        super().__init__(
            message=message,
            code="AI_PROVIDER_ERROR",
        )


class AIProviderTimeoutError(NexaAIException):
    def __init__(
        self,
        message: str = "AI provider request timed out.",
    ):
        super().__init__(
            message=message,
            code="AI_PROVIDER_TIMEOUT",
        )


class DatabaseError(NexaAIException):
    def __init__(
        self,
        message: str = "Database operation failed.",
    ):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
        )

