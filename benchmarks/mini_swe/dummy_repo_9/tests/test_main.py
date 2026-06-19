import unittest
from src.main import run_task_9

class TestMain(unittest.TestCase):
    def test_run(self):
        self.assertTrue(run_task_9())
