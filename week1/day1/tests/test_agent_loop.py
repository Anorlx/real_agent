import unittest


class AgentLoopTests(unittest.IsolatedAsyncioTestCase):
    async def test_streams_text_and_completes_without_tools(self):
        from agent.agent_loop import run_agent

        async def fake_model(messages, system_prompt, tools, model_name):
            yield {"type": "assistant_delta", "content": "hello"}
            yield {"type": "assistant_delta", "content": " world"}

        events = [
            event
            async for event in run_agent(
                user_input="hi",
                history=[],
                model_call=fake_model,
                tool_selector=None,
                max_turns=10,
            )
        ]

        self.assertEqual(
            [event["type"] for event in events],
            ["state", "state", "state", "assistant_delta", "assistant_delta", "state", "terminal"],
        )
        self.assertEqual(events[-1]["reason"], "completed")
        self.assertEqual(events[-1]["state"]["messages"][-1]["content"], "hello world")

    async def test_executes_selected_tool_and_continues_to_final_answer(self):
        from agent.agent_loop import run_agent
        from agent.tools.registry import get_tool_registry

        calls = 0

        async def fake_model(messages, system_prompt, tools, model_name):
            nonlocal calls
            calls += 1
            if calls == 1:
                yield {"type": "assistant_delta", "content": "我来算一下。"}
                yield {
                    "type": "tool_call",
                    "tool_call": {
                        "id": "tool-1",
                        "name": "calculator",
                        "arguments": {"expression": "2 + 3 * 4"},
                    },
                }
            else:
                tool_messages = [m for m in messages if m["role"] == "tool"]
                self.assertEqual(tool_messages[-1]["content"], "14")
                yield {"type": "assistant_delta", "content": "答案是 14"}

        async def fake_selector(user_input, messages, available_tools, model_name):
            self.assertEqual(model_name, "qwen3.5-flash")
            return ["calculator"]

        events = [
            event
            async for event in run_agent(
                user_input="2+3*4是多少",
                history=[],
                model_call=fake_model,
                tool_selector=fake_selector,
                tools=get_tool_registry(),
                max_turns=10,
            )
        ]

        self.assertIn("tool_result", [event["type"] for event in events])
        self.assertEqual(events[-1]["reason"], "completed")
        self.assertEqual(calls, 2)

    async def test_stops_at_max_turns_when_tools_keep_looping(self):
        from agent.agent_loop import run_agent
        from agent.tools.registry import get_tool_registry

        async def fake_model(messages, system_prompt, tools, model_name):
            yield {
                "type": "tool_call",
                "tool_call": {
                    "id": "loop",
                    "name": "calculator",
                    "arguments": {"expression": "1 + 1"},
                },
            }

        async def fake_selector(user_input, messages, available_tools, model_name):
            return ["calculator"]

        events = [
            event
            async for event in run_agent(
                user_input="keep going",
                history=[],
                model_call=fake_model,
                tool_selector=fake_selector,
                tools=get_tool_registry(),
                max_turns=2,
            )
        ]

        self.assertEqual(events[-1]["type"], "terminal")
        self.assertEqual(events[-1]["reason"], "max_turns")

    async def test_selector_failure_falls_back_instead_of_crashing(self):
        from agent.subagents.tool_search_subagent import select_tools
        from agent.tools.registry import get_tool_registry

        async def failing_model_call(messages, system_prompt, tools, model_name):
            raise RuntimeError("InvalidParameter: url error")
            yield

        selected = await select_tools(
            user_input="帮我算 1+1",
            messages=[],
            available_tools=get_tool_registry(),
            model_call=failing_model_call,
            model_name="qwen3.5-flash",
        )

        self.assertEqual(selected, ["calculator"])


if __name__ == "__main__":
    unittest.main()
