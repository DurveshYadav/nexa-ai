
from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel


# @dataclass(frozen=True)
# class ToolSpec:
#     name: str
#     description: str
#     input_schema: type[BaseModel]
#     handler: Callable
#     enabled: bool = True
#     permission: str | None = None
#     service_dependencies: tuple[str, ...] = ()

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: type[BaseModel]
    handler: Callable
    output_schema: type[BaseModel] | None = None
    enabled: bool = True
    permission: str | None = None
    service_dependencies: tuple[str, ...] = ()


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec:
        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(f"Unknown tool: {name}")

        return tool

    def list_tools(self) -> list[ToolSpec]:
        return list(self._tools.values())
