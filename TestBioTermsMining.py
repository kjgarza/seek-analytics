import unittest
from BioTermsMining import *

class TddBioTermsMining(unittest.TestCase):

    def test_get_recall(self):
        calc = Calculator()
        result = calc.add(2,2)
        self.assertEqual(4, result)

    def test_calculator_returns_error_message_if_both_args_not_numbers(self):
        self.assertRaises(ValueError, self.calc.add, 'two', 'three')

    def test_calculator_returns_error_message_if_x_arg_not_number(self):
        self.assertRaises(ValueError, self.calc.add, 'two', 3)

    def test_calculator_returns_error_message_if_x_arg_not_number(self):
        self.assertRaises(ValueError, self.calc.add, 2, 'three')

__author__ = 'kristian'
