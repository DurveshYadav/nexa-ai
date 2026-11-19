import logging
import json

from app.integrations.llm.base import BaseLLMProvider
from app.tools.v3.context import ExecutionContext
from app.tools.v3.executor import ToolExecutor
from app.tools.v3.registry import ToolRegistry
from app.services.v3.schemas.orchestrator import OrchestratorResult
from app.tools.v3.schemas.results import ToolError, ToolResult
from app.services.v3.run_manager import AgentRunManager
import time
from pydantic import ValidationError
from app.services.v3.approval_service import approval_service
from app.services.v3.schemas.execution import ExecutionStep

logger = logging.getLogger(__name__)
SENSITIVE_AGENT_TOOLS = frozenset({
    "cancel_order",
    "request_refund",
})


class AgentOrchestrator:

    def __init__(
        self,
        provider: BaseLLMProvider,
        executor: ToolExecutor,
        registry: ToolRegistry,
        tools: list[dict],
        allowed_tools: frozenset[str],
        max_iterations: int = 5,
        max_tool_calls: int = 10,
        max_consecutive_failures: int = 3,
        run_manager: AgentRunManager | None = None,
    ):
        self.provider = provider
        self.executor = executor
        self.registry = registry
        self.tools = tools
        self.allowed_tools = allowed_tools

        self.max_iterations = max_iterations
        self.max_tool_calls = max_tool_calls
        self.max_consecutive_failures = max_consecutive_failures
        self.run_manager = run_manager or AgentRunManager()


        if self.max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")

        if self.max_tool_calls < 1:
            raise ValueError("max_tool_calls must be at least 1")

        if self.max_consecutive_failures < 1:
            raise ValueError("max_consecutive_failures must be at least 1")

    def _finish_run(
        self,
        context: ExecutionContext,
        result: OrchestratorResult,
    ) -> OrchestratorResult:
        status_map = {
            "completed": "completed",
            "failed": "failed",
            "approval_required": "approval_required",
        }
        final_status = status_map[result.status]

        self.run_manager.update_status(
            run_id=context.run_id,
            user_id=context.user_id,
            status=final_status,
            error_code=result.error_code,
        )

        log_method = (
            logger.warning if result.status == "failed" else logger.info
        )
        log_method(
            "agent_run_finished run_id=%s request_id=%s "
            "status=%s iterations=%s tool_calls=%s error_code=%s",
            context.run_id,
            context.request_id,
            final_status,
            result.iterations,
            result.tool_calls_count,
            result.error_code,
        )

        return result

    def _cancelled_result(
        self,
        iteration: int,
        tool_calls_count: int,
    ) -> OrchestratorResult:
        return OrchestratorResult(
            status="failed",
            content="This agent run was cancelled.",
            iterations=iteration,
            tool_calls_count=tool_calls_count,
            error_code="RUN_CANCELLED",
        )

    def run(
        self,
        message: str,
        context: ExecutionContext,
        system_prompt: str,
    ) -> OrchestratorResult:

        self.run_manager.create_run(
            run_id=context.run_id,
            user_id=context.user_id,
        )

        self.run_manager.update_status(
            run_id=context.run_id,
            user_id=context.user_id,
            status="running",
        )

        logger.info(
            "agent_run_started run_id=%s request_id=%s user_id=%s",
            context.run_id,
            context.request_id,
            context.user_id,
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        tool_calls_count = 0
        consecutive_failures = 0

        if self.run_manager.get_run(
            context.run_id,
            context.user_id,
        ).status == "cancelled":
            logger.warning(
                "agent_run_cancelled run_id=%s request_id=%s",
                context.run_id,
                context.request_id,
            )
            return self._cancelled_result(
                0,
                tool_calls_count,
            )

        for iteration in range(1, self.max_iterations + 1):

            # 1. Ask the LLM
            try:
                response = self.provider.generate(
                    messages=messages,
                    tools=self.tools,
                )
            except Exception:
                return self._finish_run(
                    context,
                    OrchestratorResult(
                        status="failed",
                        content="The AI service is temporarily unavailable. Please try again.",
                        iterations=iteration,
                        tool_calls_count=tool_calls_count,
                        error_code="LLM_PROVIDER_ERROR",
                    ),
                )

            if self.run_manager.get_run(
                context.run_id,
                context.user_id,
            ).status == "cancelled":
                logger.warning(
                    "agent_run_cancelled run_id=%s request_id=%s",
                    context.run_id,
                    context.request_id,
                )
                return self._cancelled_result(
                    iteration,
                    tool_calls_count,
                )

            # 2. Final assistant response
            if not response.tool_calls:
                return self._finish_run(
                    context,
                    OrchestratorResult(
                        status="completed",
                        content=response.content or "I could not generate a response.",
                        iterations=iteration,
                        tool_calls_count=tool_calls_count,
                    ),
                 )

            # 3. Enforce total tool-call limit
            if tool_calls_count + len(response.tool_calls) > self.max_tool_calls:
                return self._finish_run(
                    context,
                    OrchestratorResult(
                        status="failed",
                        content="The request exceeded the maximum allowed tool calls.",
                        iterations=iteration,
                        tool_calls_count=tool_calls_count,
                        error_code="MAX_TOOL_CALLS_EXCEEDED",
                    ),
                )

           # 4. Persist approval for sensitive actions.
            sensitive_calls = [
                call for call in response.tool_calls
                if call.name in SENSITIVE_AGENT_TOOLS
            ]

            if sensitive_calls:
                if len(sensitive_calls) > 1:
                    return self._finish_run(
                        context,
                        OrchestratorResult(
                            status="failed",
                            content="Please request approval for one sensitive action at a time.",
                            iterations=iteration,
                            tool_calls_count=tool_calls_count,
                            error_code="MULTIPLE_SENSITIVE_ACTIONS",
                        ),
                    )

                if (
                    context.db is None
                    or context.conversation_id is None
                ):
                    return self._finish_run(
                        context,
                        OrchestratorResult(
                            status="failed",
                            content="Approval could not be created because the required context is missing.",
                            iterations=iteration,
                            tool_calls_count=tool_calls_count,
                            error_code="APPROVAL_CONTEXT_MISSING",
                        ),
                    )

                call = sensitive_calls[0]

                try:
                    tool = self.registry.get(call.name)

                    if not tool.enabled:
                        raise ValueError("Tool is disabled")

                    validated_arguments = tool.input_schema.model_validate(
                        call.arguments
                    )

                    approval = approval_service.create_approval(
                        db=context.db,
                        run_id=context.run_id,
                        conversation_id=context.conversation_id,
                        user_id=context.user_id,
                        tool_name=call.name,
                        arguments=validated_arguments.model_dump(
                            mode="json"
                        ),
                    )

                except ValidationError:
                    return self._finish_run(
                        context,
                        OrchestratorResult(
                            status="failed",
                            content="The sensitive action contains invalid arguments.",
                            iterations=iteration,
                            tool_calls_count=tool_calls_count,
                            error_code="INVALID_ARGUMENTS",
                        ),
                    )

                except ValueError:
                    return self._finish_run(
                        context,
                        OrchestratorResult(
                            status="failed",
                            content="The requested sensitive action is unavailable.",
                            iterations=iteration,
                            tool_calls_count=tool_calls_count,
                            error_code="SENSITIVE_TOOL_UNAVAILABLE",
                        ),
                    )

                return self._finish_run(
                    context,
                    OrchestratorResult(
                        status="approval_required",
                        content="Your approval is required before this action can proceed.",
                        iterations=iteration,
                        tool_calls_count=tool_calls_count,
                        error_code="APPROVAL_REQUIRED",
                        approval_id=approval.approval_id,
                    ),
                )

            # 5. Stop if another LLM iteration would exceed the limit
            if iteration == self.max_iterations:
                return self._finish_run(
                    context,
                    OrchestratorResult(
                        status="failed",
                        content="The request exceeded the maximum orchestration iterations.",
                        iterations=iteration,
                        tool_calls_count=tool_calls_count,
                        error_code="MAX_ITERATIONS_EXCEEDED",
                    ),
                )

            # 6. Add assistant tool-call message
            messages.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": json.dumps(call.arguments),
                        },
                    }
                    for call in response.tool_calls
                ],
            })

            # 7. Execute requested tools.
            for call in response.tool_calls:

                step_number = len(
                    self.run_manager.get_history(
                        context.run_id,
                        context.user_id,
                    )
                ) + 1

                started_at = time.perf_counter()
                logger.info(
                    "agent_tool_started run_id=%s request_id=%s "
                    "tool_name=%s iteration=%s",
                    context.run_id,
                    context.request_id,
                    call.name,
                    iteration,
                )
                try:
                    self.registry.get(call.name)
                except ValueError:
                    # Unknown tools are handled by ToolExecutor.
                    pass
                else:
                    if call.name not in self.allowed_tools:
                        tool_result = ToolResult(
                            success=False,
                            error=ToolError(
                                code="TOOL_NOT_ALLOWED",
                                message="This tool is not available to the agent.",
                            ),
                        )
                        # Skip execution for disallowed tools.
                        messages.append({
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(
                                tool_result.model_dump(mode="json")
                            ),
                        })

                        duration_ms = (time.perf_counter() - started_at) * 1000
                        if tool_result.success:
                            logger.info(
                                "agent_tool_completed run_id=%s request_id=%s "
                                "tool_name=%s duration_ms=%.2f",
                                context.run_id,
                                context.request_id,
                                call.name,
                                duration_ms,
                            )
                        else:
                            logger.warning(
                                "agent_tool_failed run_id=%s request_id=%s "
                                "tool_name=%s error_code=%s duration_ms=%.2f",
                                context.run_id,
                                context.request_id,
                                call.name,
                                tool_result.error.code if tool_result.error else "UNKNOWN",
                                duration_ms,
                            )
                        self.run_manager.add_step(
                            run_id=context.run_id,
                            user_id=context.user_id,
                            step=ExecutionStep(
                                step_number=step_number,
                                tool_call_id=call.id,
                                tool_name=call.name,
                                status="completed" if tool_result.success else "failed",
                                error_code=(
                                    tool_result.error.code
                                    if tool_result.error
                                    else None
                                ),
                                duration_ms=duration_ms,
                            ),
                        )

                        self.run_manager.update_progress(
                            run_id=context.run_id,
                            user_id=context.user_id,
                            iteration=iteration,
                            tool_calls_count=tool_calls_count + 1,
                            current_tool=call.name,
                        )
                        tool_calls_count += 1
                        consecutive_failures += 1

                        if consecutive_failures >= self.max_consecutive_failures:
                            return self._finish_run(
                                context,
                                OrchestratorResult(
                                    status="failed",
                                    content="The request stopped after repeated tool execution failures.",
                                    iterations=iteration,
                                    tool_calls_count=tool_calls_count,
                                    error_code="MAX_CONSECUTIVE_FAILURES",
                                ),
                            )

                        continue

                try:
                    tool_result = self.executor.execute(
                        tool_name=call.name,
                        arguments=call.arguments,
                        context=context,
                    )
                except Exception:
                    tool_result = ToolResult(
                        success=False,
                        error=ToolError(
                            code="EXECUTION_ERROR",
                            message="The tool could not be executed.",
                        ),
                    )


                duration_ms = (time.perf_counter() - started_at) * 1000

                self.run_manager.add_step(
                    run_id=context.run_id,
                    user_id=context.user_id,
                    step=ExecutionStep(
                        step_number=step_number,
                        tool_call_id=call.id,
                        tool_name=call.name,
                        status="completed" if tool_result.success else "failed",
                        error_code=(
                            tool_result.error.code
                            if tool_result.error
                            else None
                        ),
                        duration_ms=duration_ms,
                    ),
                )

                self.run_manager.update_progress(
                    run_id=context.run_id,
                    user_id=context.user_id,
                    iteration=iteration,
                    tool_calls_count=tool_calls_count + 1,
                    current_tool=call.name,
                )

                tool_calls_count += 1

                if tool_result.success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(
                        tool_result.model_dump(mode="json")
                    ),
                })

                if consecutive_failures >= self.max_consecutive_failures:
                    return self._finish_run(
                        context,
                        OrchestratorResult(
                            status="failed",
                            content="The request stopped after repeated tool execution failures.",
                            iterations=iteration,
                            tool_calls_count=tool_calls_count,
                            error_code="MAX_CONSECUTIVE_FAILURES",
                        ),
                    )


        return self._finish_run(
            context,
            OrchestratorResult(
                status="failed",
                content="Unable to complete the request.",
                iterations=self.max_iterations,
                tool_calls_count=tool_calls_count,
                error_code="ORCHESTRATION_FAILED",
            ),
        )
