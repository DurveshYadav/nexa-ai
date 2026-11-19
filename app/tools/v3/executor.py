
from pydantic import ValidationError

from app.tools.v3.registry import ToolRegistry
from app.tools.v3.dependencies import ToolDependencies
from app.tools.v3.context import ExecutionContext
from app.tools.v3.schemas.results import ToolResult, ToolError


class ToolExecutor:

    def __init__(
        self,
        registry: ToolRegistry,
        dependencies: ToolDependencies,
    ):
        self.registry = registry
        self.dependencies = dependencies

    def execute(
        self,
        tool_name: str,
        arguments: dict,
        context: ExecutionContext,
    ) -> ToolResult:

        # 1. Registry lookup
        try:
            tool = self.registry.get(tool_name)
        except ValueError:
            return self._error(
                "UNKNOWN_TOOL",
                "Requested tool is not registered.",
            )

        # 2. Enabled check
        if not tool.enabled:
            return self._error(
                "TOOL_DISABLED",
                "Requested tool is disabled.",
            )

        # 3. Validate arguments
        try:
            validated_arguments = tool.input_schema.model_validate(
                arguments
            )
        except ValidationError:
            return self._error(
                "INVALID_ARGUMENTS",
                "The supplied tool arguments are invalid.",
            )

        # 4. Permission check
        if (
            tool.permission
            and tool.permission not in context.permissions
        ):
            return self._error(
                "PERMISSION_DENIED",
                "You do not have permission to execute this tool.",
            )

        # 5. Inject declared service dependencies
        try:
            service_kwargs = {
                service_name: getattr(
                    self.dependencies,
                    service_name,
                )
                for service_name in tool.service_dependencies
            }

            # 6. Execute handler
            result = tool.handler(
                arguments=validated_arguments,
                context=context,
                **service_kwargs,
            )

            # if not isinstance(result, ToolResult):
            #     return self._error(
            #         "EXECUTION_ERROR",
            #         "Tool returned an invalid response.",
            #     )

            # return result

            if not isinstance(result, ToolResult):
                return self._error(
                    "EXECUTION_ERROR",
                    "Tool returned an invalid response.",
                )

            # 7. Validate handler output
            if tool.output_schema:
                if result.success and result.data is None:
                    return self._error(
                        "INVALID_TOOL_OUTPUT",
                        "Successful tool returned no data.",
                    )

                if result.data is not None:
                    try:
                        validated_output = tool.output_schema.model_validate(
                            result.data
                        )
                    except ValidationError:
                        return self._error(
                            "INVALID_TOOL_OUTPUT",
                            "Tool returned data that does not match its output schema.",
                        )

                    return ToolResult(
                        success=result.success,
                        data=validated_output.model_dump(),
                        error=result.error,
                    )

            return result


        except Exception:
            return self._error(
                "EXECUTION_ERROR",
                "Tool execution failed.",
            )

    @staticmethod
    def _error(code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            error=ToolError(
                code=code,
                message=message,
            ),
        )
