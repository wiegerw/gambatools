#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase

from gambatools.regexp import *
from gambatools.regexp_parser import parse_regexp
from gambatools.regexp_simple_parser import parse_simple_regexp


__author__      = "Wieger Wesselink"
__copyright__   = "Copyright 2020, Automata project"
__credits__     = ["Erik de Vink", "Wieger Wesselink"]
__license__     = "To be determined"
__version__     = "0.1"
__maintainer__  = "Wieger Wesselink"
__email__       = "j.w.wesselink@tue.nl"
__status__      = "Development"


class Test(TestCase):
    def regexp_print_text(self, x: Regexp, expected_result: str):
        result = str(x)
        self.assertEqual(expected_result, result)

    def test_regexp_print(self):
        self.regexp_print_text(Zero(), '0')
        self.regexp_print_text(One(), '1')
        self.regexp_print_text(Sum(One(), Zero()), '1 + 0')
        self.regexp_print_text(Iteration(Sum(One(), Zero())), '(1 + 0)*')

    def _parse_print_test(self, text: str, expected_result: str = None, simple: bool = False):
        if not expected_result:
            expected_result = text
        x = parse_simple_regexp(text) if simple else parse_regexp(text)
        result = str(x)
        self.assertEqual(expected_result, result)

    def test_parse_print(self):
        self._parse_print_test('0')
        self._parse_print_test('0 + 1')
        self._parse_print_test('a')
        self._parse_print_test('a* + b')
        self._parse_print_test('(a* + b)** + b + a*')
        self._parse_print_test('a . b . c')
        self._parse_print_test('abc', 'a . b . c', simple=True)


if __name__ == '__main__':
    import unittest
    unittest.main()
