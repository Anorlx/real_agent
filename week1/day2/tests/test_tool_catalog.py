import unittest


class ToolCatalogTests(unittest.IsolatedAsyncioTestCase):
    def test_tool_catalog_readme_covers_registered_tools(self):
        from agent.tools.registry import get_tool_registry, tool_catalog_text

        catalog = tool_catalog_text()
        tools = get_tool_registry()

        for name in tools:
            self.assertIn(f"`{name}`", catalog)

    async def test_tool_selector_prompt_uses_readme_catalog_not_full_schema(self):
        from agent.subagents.tool_search_subagent import select_tools
        from agent.tools.registry import get_tool_registry

        captured = {}

        async def fake_model_call(messages, system_prompt, tools, model_name):
            captured["content"] = messages[0]["content"]
            yield {"type": "assistant_delta", "content": '{"tools":["calculator"]}'}

        selected = await select_tools(
            user_input="算一下 1+1",
            messages=[],
            available_tools=get_tool_registry(),
            model_call=fake_model_call,
        )

        self.assertEqual(selected, ["calculator"])
        self.assertIn("tool_catalog", captured["content"])
        self.assertIn("agent/tools/calculator.py", captured["content"])
        self.assertNotIn('"parameters"', captured["content"])

    def test_tool_catalog_mentions_command_and_permission_reviewer(self):
        from agent.tools.registry import tool_catalog_text

        catalog = tool_catalog_text()

        self.assertIn("`run_command`", catalog)
        self.assertIn("agent/tools/command.py", catalog)
        self.assertIn("permission_review_subagent", catalog)


if __name__ == "__main__":
    unittest.main()
