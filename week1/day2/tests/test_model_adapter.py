import unittest
from pathlib import Path


class ModelAdapterTests(unittest.TestCase):
    def test_dashscope_client_source_file_exists(self):
        root = Path(__file__).resolve().parents[1]

        self.assertTrue((root / "agent" / "models" / "dashscope_client.py").exists())


if __name__ == "__main__":
    unittest.main()
