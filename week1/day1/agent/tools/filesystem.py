from __future__ import annotations

from pathlib import Path
from typing import Any


def _resolve_inside_workspace(path: str, workspace_root: Path | None = None) -> Path:
    root = (workspace_root or Path.cwd()).resolve()
    target = (root / path).resolve()
    if target != root and root not in target.parents:
        raise ValueError("Path is outside workspace.")
    return target


async def read_file(
    arguments: dict[str, Any],
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    try:
        path = _resolve_inside_workspace(str(arguments.get("path", "")), workspace_root)
        return {"ok": True, "content": path.read_text(encoding="utf-8")}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


async def write_file(
    arguments: dict[str, Any],
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    try:
        path = _resolve_inside_workspace(str(arguments.get("path", "")), workspace_root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(arguments.get("content", "")), encoding="utf-8")
        return {"ok": True, "content": f"Wrote {path.name}"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


async def list_dir(
    arguments: dict[str, Any],
    workspace_root: Path | None = None,
) -> dict[str, Any]:
    try:
        path = _resolve_inside_workspace(str(arguments.get("path", ".")), workspace_root)
        entries = sorted(child.name for child in path.iterdir())
        return {"ok": True, "entries": entries, "content": "\n".join(entries)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def read_file_spec() -> dict[str, Any]:
    return {
        "name": "read_file",
        "description": "读取 agent_write 工作区内的文本文件内容。不能读取工作区之外的路径。",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "相对 agent_write 的文件路径。"}},
            "required": ["path"],
        },
    }


def write_file_spec() -> dict[str, Any]:
    return {
        "name": "write_file",
        "description": "写入 agent_write 工作区内的文本文件，会自动创建父目录。不能写到工作区之外。",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "相对 agent_write 的文件路径。"},
                "content": {"type": "string", "description": "要写入的文本内容。"},
            },
            "required": ["path", "content"],
        },
    }


def list_dir_spec() -> dict[str, Any]:
    return {
        "name": "list_dir",
        "description": "列出 agent_write 工作区内目录的文件名。",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "相对 agent_write 的目录路径。"}},
            "required": ["path"],
        },
    }

