
from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        """Generate an LLM response, optionally using tools."""
        raise NotImplementedError
