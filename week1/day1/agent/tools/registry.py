from __future__ import annotations

from pathlib import Path
from typing import Any, Awaitable, Callable

from agent.config import DEFAULT_TOOL_WORKSPACE, PROJECT_ROOT
from agent.tools.calculator import calculator, calculator_spec
from agent.tools.filesystem import (
    list_dir,
    list_dir_spec,
    read_file,
    read_file_spec,
    write_file,
    write_file_spec,
)
from agent.tools.project import (
    grep_project,
    grep_project_spec,
    ls_project,
    ls_project_spec,
    read_project_file,
    read_project_file_spec,
)
from agent.tools.time_tool import current_time, current_time_spec

ToolFunc = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
TOOL_CATALOG_PATH = Path(__file__).with_name("README.md")


def _with_workspace(func: Callable[..., Awaitable[dict[str, Any]]], root: Path) -> ToolFunc:
    async def run(arguments: dict[str, Any]) -> dict[str, Any]:
        return await func(arguments, workspace_root=root)

    return run


def _with_project(func: Callable[..., Awaitable[dict[str, Any]]], root: Path) -> ToolFunc:
    async def run(arguments: dict[str, Any]) -> dict[str, Any]:
        return await func(arguments, project_root=root)

    return run


def get_tool_registry(workspace_root: Path | None = None) -> dict[str, dict[str, Any]]:
    root = (workspace_root or DEFAULT_TOOL_WORKSPACE).resolve()
    root.mkdir(parents=True, exist_ok=True)
    project_root = PROJECT_ROOT.resolve()
    return {
        "read_file": {"spec": read_file_spec(), "run": _with_workspace(read_file, root)},
        "write_file": {"spec": write_file_spec(), "run": _with_workspace(write_file, root)},
        "list_dir": {"spec": list_dir_spec(), "run": _with_workspace(list_dir, root)},
        "ls_project": {"spec": ls_project_spec(), "run": _with_project(ls_project, project_root)},
        "grep_project": {"spec": grep_project_spec(), "run": _with_project(grep_project, project_root)},
        "read_project_file": {
            "spec": read_project_file_spec(),
            "run": _with_project(read_project_file, project_root),
        },
        "calculator": {"spec": calculator_spec(), "run": calculator},
        "current_time": {"spec": current_time_spec(), "run": current_time},
    }


def tool_descriptions(tools: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {"name": name, "description": info["spec"]["description"]}
        for name, info in tools.items()
    ]


def tool_catalog_text() -> str:
    return TOOL_CATALOG_PATH.read_text(encoding="utf-8")


def dashscope_tool_specs(selected_names: list[str], tools: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    specs = []
    for name in selected_names:
        if name in tools:
            spec = tools[name]["spec"]
            specs.append({"type": "function", "function": spec})
    return specs
