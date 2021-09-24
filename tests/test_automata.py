#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase
from gambatools.dfa_algorithms import random_dfa, dfa_minimize
from gambatools.dfa import Symbol
from gambatools.automaton_algorithms import parse_automaton
from gambatools.draw_sigma import automaton_to_sigma


class TestAutomaton(TestCase):
    def test_check_validity(self):
        text = '''
            initial q0
            final q1
            states q0 q1
            q0 q0 a
            q0 q1 b
            q1 q0 a
        '''
        A = parse_automaton(text)
        html = automaton_to_sigma(A)


if __name__ == '__main__':
    import unittest
    unittest.main()
