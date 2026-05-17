import unittest
from pathlib import Path


class MainEntryTests(unittest.TestCase):
    def test_main_module_exposes_cli_entrypoint(self):
        import main

        self.assertTrue(callable(main.main))

    def test_default_tool_workspace_is_agent_write(self):
        from agent.config import DEFAULT_TOOL_WORKSPACE

        expected = Path(__file__).resolve().parents[1] / "agent_write"
        self.assertEqual(DEFAULT_TOOL_WORKSPACE, expected)


if __name__ == "__main__":
    unittest.main()
