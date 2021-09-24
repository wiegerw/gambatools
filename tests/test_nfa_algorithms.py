#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase

from gambatools.cfg_algorithms import parse_cfg_baeten, cfg_to_nfa
from gambatools.dfa_algorithms import dfa_words_up_to_n
from gambatools.nfa_algorithms import nfa_accepts_word, nfa_words_up_to_n, nfa_to_dfa, random_nfa, \
    parse_nfa
from gambatools.dfa import Symbol
from gambatools.nfa import NFA
from gambatools.printing import print_words


class Test(TestCase):
    def test_nfa_accepts_word(self):
        grammar = '''
            S = aT + bU
            T = U + bV
            U = aV + V
            V = bV + 1
        '''
        N: NFA = parse_nfa_baeten(grammar)
        self.assertTrue(nfa_accepts_word(N, 'a'))
        self.assertTrue(nfa_accepts_word(N, 'ab'))
        self.assertTrue(nfa_accepts_word(N, 'abb'))
        self.assertTrue(nfa_accepts_word(N, 'b'))
        self.assertTrue(nfa_accepts_word(N, 'bb'))
        self.assertTrue(nfa_accepts_word(N, 'aab'))
        self.assertTrue(nfa_accepts_word(N, 'aa'))
        self.assertTrue(nfa_accepts_word(N, 'bab'))
        self.assertFalse(nfa_accepts_word(N, 'aba'))

    def test_nfa_parse(self):
        # Sipser exercise 1.7bc
        grammar = '''
            initial s0
            final s4
            states s0 s1 s2 s3 s4
            s0 s0 0 1
            s0 s1 0
            s1 s2 1
            s2 s3 0
            s3 s4 1
            s4 s4 0 1
        '''
        N: NFA = parse_nfa(grammar)
        self.assertTrue(nfa_accepts_word(N, '000101'))

        # Sipser exercise 1.10a
        grammar = '''
            initial s4
            final s4
            states s0 s1 s2 s3 s4
            epsilon _
            s0 s0 0
            s0 s1 1
            s1 s1 0
            s1 s2 1
            s2 s2 0
            s2 s3 1
            s3 s3 0 1
            s3 s4 _
            s4 s0 _
        '''
        N: NFA = parse_nfa(grammar)
        self.assertFalse(nfa_accepts_word(N, '000101'))
        self.assertFalse(nfa_accepts_word(N, '01'))
        self.assertTrue(nfa_accepts_word(N, '0001011'))

        grammar = """
            initial 1
            final 1
            1 2 b
            1 3 _
            2 2 a
            2 3 a b
            3 1 a
        """
        N: NFA = parse_nfa(grammar)
        self.assertTrue(nfa_accepts_word(N, 'abaa'))

    def test_nfa_to_dfa(self):
        for i in range(100):
            print('test_nfa_to_dfa {}'.format(i))
            N = random_nfa({Symbol('a'), Symbol('b')}, 5)
            D = nfa_to_dfa(N)
            n = 4
            wordsD = dfa_words_up_to_n(D, n)
            wordsN = nfa_words_up_to_n(N, n)
            if wordsD != wordsN:
                print(N)
                print(D)
                print('words_up_to_n(D, {}) = {}'.format(n, print_words(wordsD)))
                print('words_up_to_n(N, {}) = {}'.format(n, print_words(wordsN)))
            self.assertEqual(wordsD, wordsN)


def parse_nfa_baeten(text: str) -> NFA:
    G = parse_cfg_baeten(text)
    return cfg_to_nfa(G)


if __name__ == '__main__':
    import unittest
    unittest.main()
