import unittest
from src.utils import reverse_string

class TestUtils(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse_string("hello"), "olleh")
