import unittest
from io import StringIO


class InputTests(unittest.IsolatedAsyncioTestCase):
    async def test_prompt_reader_strips_input(self):
        from agent.input import TerminalInput

        class FakeSession:
            async def prompt_async(self):
                return "  你好  "

        reader = TerminalInput(session=FakeSession())

        self.assertEqual(await reader.read(), "你好")

    def test_prompt_toolkit_reader_is_available(self):
        from unittest.mock import patch

        from agent.input import create_terminal_input

        with patch("sys.stdin.isatty", return_value=True):
            reader = create_terminal_input()

        self.assertEqual(reader.name, "prompt_toolkit")

    def test_pipe_input_uses_fallback_reader(self):
        from unittest.mock import patch

        from agent.input import create_terminal_input

        with patch("sys.stdin.isatty", return_value=False):
            reader = create_terminal_input()

        self.assertEqual(reader.name, "input")

    async def test_fallback_reader_reads_piped_stdin(self):
        from unittest.mock import patch

        from agent.input import FallbackInput

        with patch("sys.stdin", StringIO("exit\n")):
            reader = FallbackInput(prompt="")
            text = await reader.read()

        self.assertEqual(text, "exit")


if __name__ == "__main__":
    unittest.main()
