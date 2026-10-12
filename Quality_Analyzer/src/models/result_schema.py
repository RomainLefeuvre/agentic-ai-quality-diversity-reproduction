from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict


@dataclass
class ToolResult:
    """
    Result produced by a single analyzer.
    """

    status: str = "success"
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectResult:

    project_id: str
    language: str
    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    tools: Dict[str, ToolResult] = field(default_factory=dict)

    def add_tool_result(
        self,
        tool_name: str,
        result: ToolResult
    ) -> None:
        self.tools[tool_name] = result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "language": self.language,
            "timestamp": self.timestamp,
            "tools": {
                tool_name: tool_result.to_dict()
                for tool_name, tool_result in self.tools.items()
            }
        }