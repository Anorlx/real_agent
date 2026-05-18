import io
import unittest
from contextlib import redirect_stdout


class CliOutputTests(unittest.TestCase):
    def test_tool_result_output_hides_file_content(self):
        from agent.cli import _print_event

        event = {
            "type": "tool_result",
            "message": {
                "name": "read_project_file",
                "arguments": {"path": "agent/agent_loop.py"},
                "content": "SECRET FILE CONTENT",
                "summary": "path=agent/agent_loop.py",
            },
        }
        output = io.StringIO()

        with redirect_stdout(output):
            _print_event(event)

        text = output.getvalue()
        self.assertIn("read_project_file", text)
        self.assertIn("agent/agent_loop.py", text)
        self.assertNotIn("SECRET FILE CONTENT", text)

    def test_tool_call_output_hides_large_content_argument(self):
        from agent.cli import _print_event

        event = {
            "type": "tool_call",
            "tool_call": {
                "name": "write_file",
                "arguments": {"path": "notes/a.txt", "content": "x" * 500},
            },
        }
        output = io.StringIO()

        with redirect_stdout(output):
            _print_event(event)

        text = output.getvalue()
        self.assertIn("write_file", text)
        self.assertIn("notes/a.txt", text)
        self.assertIn("content=500 chars", text)
        self.assertNotIn("x" * 100, text)

