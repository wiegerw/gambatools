#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase

from gambatools.automaton import Automaton
from gambatools.automaton_algorithms import parse_automaton


class Test(TestCase):
    def test_automaton_builder(self):
        grammar = '''
            initial q0
            final q1
            states q0 q1
            q0 q0 a
            q0 q1 b
            q1 q0 a
        '''
        A: Automaton = parse_automaton(grammar)


if __name__ == '__main__':
    import unittest
    unittest.main()
