import tempfile
import unittest
from pathlib import Path
import sys


class ToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_calculator_rejects_unsafe_code(self):
        from agent.tools.calculator import calculator

        result = await calculator({"expression": "__import__('os').system('echo nope')"})

        self.assertFalse(result["ok"])
        self.assertIn("Only arithmetic expressions", result["error"])

    async def test_filesystem_tools_read_write_delete_and_list_inside_root(self):
        from agent.tools.filesystem import delete_file, list_dir, read_file, write_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            write_result = await write_file(
                {"path": "notes/hello.txt", "content": "hello"},
                workspace_root=root,
            )
            read_result = await read_file(
                {"path": "notes/hello.txt"},
                workspace_root=root,
            )
            list_result = await list_dir({"path": "notes"}, workspace_root=root)
            delete_result = await delete_file(
                {"path": "notes/hello.txt"},
                workspace_root=root,
            )

        self.assertTrue(write_result["ok"])
        self.assertEqual(read_result["content"], "hello")
        self.assertEqual(list_result["entries"], ["hello.txt"])
        self.assertTrue(delete_result["ok"])
        self.assertFalse((root / "notes" / "hello.txt").exists())

    async def test_filesystem_tools_block_path_escape(self):
        from agent.tools.filesystem import delete_file, read_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = await read_file({"path": "../outside.txt"}, workspace_root=root)
            delete_result = await delete_file({"path": "../outside.txt"}, workspace_root=root)

        self.assertFalse(result["ok"])
        self.assertIn("outside project", result["error"])
        self.assertFalse(delete_result["ok"])
        self.assertIn("outside project", delete_result["error"])

    async def test_project_ls_grep_and_read_are_limited_to_project_root(self):
        from agent.tools.project import grep_project, ls_project, read_project_file

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "agent").mkdir()
            (root / "agent" / "demo.py").write_text("needle = 42\n", encoding="utf-8")
            (root / "README.md").write_text("hello project\n", encoding="utf-8")

            ls_result = await ls_project({"path": "."}, project_root=root)
            grep_result = await grep_project({"pattern": "needle"}, project_root=root)
            read_result = await read_project_file({"path": "agent/demo.py"}, project_root=root)
            escape_result = await read_project_file({"path": "../secret.txt"}, project_root=root)

        self.assertTrue(ls_result["ok"])
        self.assertIn("README.md", ls_result["entries"])
        self.assertTrue(grep_result["ok"])
        self.assertEqual(grep_result["matches"][0]["path"], "agent/demo.py")
        self.assertEqual(read_result["content"], "needle = 42\n")
        self.assertFalse(escape_result["ok"])
        self.assertIn("outside project", escape_result["error"])

    async def test_project_tools_are_registered(self):
        from agent.tools.registry import get_tool_registry

        tools = get_tool_registry()

        self.assertIn("ls_project", tools)
        self.assertIn("grep_project", tools)
        self.assertIn("read_project_file", tools)

    async def test_tool_metadata_marks_parallel_safety(self):
        from agent.tools.registry import get_tool_registry

        tools = get_tool_registry()

        self.assertEqual(tools["read_file"]["category"], "文件")
        self.assertTrue(tools["read_file"]["parallel_safe"])
        self.assertFalse(tools["write_file"]["parallel_safe"])
        self.assertFalse(tools["delete_file"]["parallel_safe"])
        self.assertEqual(tools["grep_project"]["category"], "搜索")
        self.assertTrue(tools["grep_project"]["parallel_safe"])

    async def test_file_tools_default_to_project_root(self):
        from agent.config import PROJECT_ROOT
        from agent.tools.registry import get_tool_registry

        tools = get_tool_registry()

        result = await tools["write_file"]["run"](
            {"path": "agent_write/registry_permission_probe.txt", "content": "probe"}
        )
        cleanup = await tools["delete_file"]["run"](
            {"path": "agent_write/registry_permission_probe.txt"}
        )

        self.assertTrue(result["ok"])
        self.assertTrue(cleanup["ok"])
        self.assertFalse((PROJECT_ROOT / "agent_write" / "registry_permission_probe.txt").exists())

    async def test_run_command_executes_code_inside_project(self):
        from agent.tools.command import run_command

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "hello.py"
            script.write_text("print('hello from tool')\n", encoding="utf-8")

            result = await run_command(
                {"command": [sys.executable, "hello.py"], "cwd": ".", "timeout": 5},
                project_root=root,
            )

        self.assertTrue(result["ok"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["stdout"].strip(), "hello from tool")

    async def test_run_command_blocks_cwd_escape(self):
        from agent.tools.command import run_command

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = await run_command(
                {"command": [sys.executable, "-c", "print('nope')"], "cwd": ".."},
                project_root=root,
            )

        self.assertFalse(result["ok"])
        self.assertIn("outside project", result["error"])

    async def test_command_tool_is_registered_as_unsafe_execution(self):
        from agent.tools.registry import get_tool_registry

        tools = get_tool_registry()

        self.assertIn("run_command", tools)
        self.assertEqual(tools["run_command"]["category"], "执行")
        self.assertFalse(tools["run_command"]["parallel_safe"])


if __name__ == "__main__":
    unittest.main()
