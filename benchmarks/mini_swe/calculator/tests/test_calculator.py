import unittest
from src.calculator import divide, add

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        
    def test_divide_zero(self):
        with self.assertRaises(ValueError):
            divide(10, 0)
