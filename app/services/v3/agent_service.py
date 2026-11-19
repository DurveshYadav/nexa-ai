
from app.integrations.llm.base import BaseLLMProvider
from app.integrations.llm.openai_provider import OpenAIProvider
from app.prompts.v3.support_agent import SUPPORT_AGENT_SYSTEM_PROMPT
from app.services.v3.orchestrator import AgentOrchestrator
from app.tools.v3.context import ExecutionContext
from app.tools.v3.dependencies import ToolDependencies
from app.tools.v3.executor import ToolExecutor
from app.tools.v3.registration import (
    build_tool_registry,
    get_llm_tool_definitions,
)
from app.tools.v3.registry import ToolRegistry

# Sensitive actions remain unavailable until approval enforcement exists.
ALLOWED_AGENT_TOOLS = frozenset({
    "get_order_status",
    "get_order_details",
    "get_product_details",
    "check_product_availability",
    "get_customer_profile",
    "create_support_ticket",
    "check_refund_eligibility",
})


class AgentService:

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
        registry: ToolRegistry | None = None,
        dependencies: ToolDependencies | None = None,
        max_tool_iterations: int = 5,
        max_tool_calls: int = 10,
        max_consecutive_failures: int = 3,
    ):
        self.provider = provider or OpenAIProvider()
        self.registry = registry or build_tool_registry()
        self.dependencies = dependencies or ToolDependencies()

        self.executor = ToolExecutor(
            registry=self.registry,
            dependencies=self.dependencies,
        )

        registered_tools = get_llm_tool_definitions(self.registry)

        self.tools = [
            tool
            for tool in registered_tools
            if tool["function"]["name"] in ALLOWED_AGENT_TOOLS
        ]

        self.orchestrator = AgentOrchestrator(
            provider=self.provider,
            executor=self.executor,
            registry=self.registry,
            tools=self.tools,
            allowed_tools=ALLOWED_AGENT_TOOLS,
            max_iterations=max_tool_iterations,
            max_tool_calls=max_tool_calls,
            max_consecutive_failures=max_consecutive_failures,
        )

    def chat(
        self,
        message: str,
        context: ExecutionContext,
    ) -> str:

        result = self.orchestrator.run(
            message=message,
            context=context,
            system_prompt=SUPPORT_AGENT_SYSTEM_PROMPT,
        )

        return result.content

    def run(self, message: str, context: ExecutionContext):
        return self.orchestrator.run(
            message=message,
            context=context,
            system_prompt=SUPPORT_AGENT_SYSTEM_PROMPT,
        )

    def chat(self, message: str, context: ExecutionContext) -> str:
        return self.run(message=message, context=context).content
