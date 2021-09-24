#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase

from gambatools.cfg import CFG
from gambatools.cfg_algorithms import parse_cfg_baeten


class TestCFG(TestCase):
    def test_is_chomsky(self):
        grammar = '''
            S = aS + bT
            T = aS + bT + 1
        '''
        G: CFG = parse_cfg_baeten(grammar)
        self.assertFalse(G.is_chomsky())

        grammar = '''
            S = ST + b
            T = TT + a
        '''
        G: CFG = parse_cfg_baeten(grammar)
        self.assertFalse(G.is_chomsky())

        grammar = '''
            S = TT + b
            T = TT + 1
        '''
        G: CFG = parse_cfg_baeten(grammar)
        self.assertFalse(G.is_chomsky())

        grammar = '''
            S = TT + b
            T = TT + a
        '''
        G: CFG = parse_cfg_baeten(grammar)
        self.assertTrue(G.is_chomsky())

    def test_is_valid(self):
        grammar = '''
            S = aS + bT
            T = aS + bT + 1
        '''
        G: CFG = parse_cfg_baeten(grammar, check_validity=False)
        self.assertTrue(G.is_valid())

        grammar = '''
            S = aS + bT
            T = aS + bT + 1
            T = aS + bT + 1
        '''
        G: CFG = parse_cfg_baeten(grammar, check_validity=False)
        self.assertTrue(G.is_valid())  # TODO: should this test fail?

        grammar = '''
            S = aS + bT
            T = aU + bT + 1
        '''
        G: CFG = parse_cfg_baeten(grammar, check_validity=False)
        self.assertFalse(G.is_valid())


if __name__ == '__main__':
    import unittest
    unittest.main()
