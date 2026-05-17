from __future__ import annotations

import argparse
import asyncio
from typing import Any

from agent.agent_loop import run_agent
from agent.config import DEFAULT_TOOL_WORKSPACE
from agent.input import create_terminal_input, patch_stdout_context
from agent.models.main_agent import dashscope_stream_chat
from agent.subagents.tool_search_subagent import select_tools
from agent.tools.registry import get_tool_registry


def _print_event(event: dict[str, Any]) -> None:
    event_type = event["type"]
    if event_type == "state":
        state = event["state"]
        print(f"\n[state] turn={state['turn']} phase={event['phase']}")
    elif event_type == "assistant_delta":
        print(event["content"], end="", flush=True)
    elif event_type == "tool_call":
        tool_call = event["tool_call"]
        print(f"\n[tool_call] {tool_call.get('name')} {tool_call.get('arguments')}")
    elif event_type == "tool_result":
        message = event["message"]
        print(f"\n[tool_result] {message['name']}: {message['content']}")
    elif event_type == "terminal":
        print(f"\n[terminal] {event['reason']}: {event['message']}")


async def _selector(
    user_input: str,
    messages: list[dict[str, Any]],
    available_tools: dict[str, dict[str, Any]],
    model_name: str,
) -> list[str]:
    return await select_tools(
        user_input=user_input,
        messages=messages,
        available_tools=available_tools,
        model_call=dashscope_stream_chat,
        model_name=model_name,
    )


async def chat_loop(max_turns: int) -> None:
    history: list[dict[str, Any]] = []
    tools = get_tool_registry(DEFAULT_TOOL_WORKSPACE)
    reader = create_terminal_input()
    print("agent started. 输入 exit/quit 结束。")
    print(f"tool workspace: {DEFAULT_TOOL_WORKSPACE}")
    print(f"input mode: {reader.name}")
    while True:
        try:
            user_input = await reader.read()
        except (EOFError, KeyboardInterrupt):
            print("\n[terminal] aborted_streaming")
            return
        if user_input.lower() in {"exit", "quit"}:
            print("[terminal] completed")
            return
        if not user_input:
            continue

        last_state = None
        async for event in run_agent(
            user_input=user_input,
            history=history,
            model_call=dashscope_stream_chat,
            tool_selector=_selector,
            tools=tools,
            max_turns=max_turns,
        ):
            _print_event(event)
            if "state" in event:
                last_state = event["state"]
        if last_state is not None:
            history = last_state["messages"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the minimal async agent.")
    parser.add_argument("--max-turns", type=int, default=10)
    args = parser.parse_args()
    with patch_stdout_context()():
        asyncio.run(chat_loop(args.max_turns))
