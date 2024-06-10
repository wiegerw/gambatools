#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random

from unittest import TestCase

from gambatools.cfg_algorithms import parse_cfg_baeten, cfg_to_dfa
from gambatools.dfa_algorithms import dfa_accepts_word, dfa_words_up_to_n, random_dfa, \
    dfa_minimize, dfa_simulate_word, parse_dfa, dfa_isomorphic, dfa_isomorphic1, dfa_hopfcroft, dfa_quotient
from gambatools.dfa_io import draw_dfa
from gambatools.nfa_algorithms import nfa_words_up_to_n
from gambatools.dfa import State, Symbol, DFA
from gambatools.regexp import Regexp
from gambatools.regexp_algorithms import regexp_to_nfa, regexp_words_up_to_n, dfa_to_regexp
from gambatools.printing import print_words
from gambatools.global_settings import GambaTools


def permute_dfa_states(D: DFA) -> DFA:
    states = list(D.Q)
    states1 = random.sample(states, k=len(states))
    sigma = {states[i]:states1[i] for i in range(len(states))}

    Q = set(states)
    F = set(sigma[q] for q in D.F)
    q0 = sigma[D.q0]
    Sigma = D.Sigma
    delta = {(sigma[q1], a):sigma[q2] for (q1, a), q2 in D.delta.items()}
    return DFA(Q, Sigma, delta, q0, F)


class Test(TestCase):
    def test_dfa_is_total(self):
        grammar = '''
            S = aS + bT
            T = aS + bT + 1
        '''
        D: DFA = parse_dfa_baeten(grammar, False)
        self.assertTrue(D._is_total())

        grammar = '''
            initial q0
            final q1
            states q0 q1
            q0 q0 a
            q0 q1 b
            q1 q0 a
        '''
        with self.assertRaises(RuntimeError) as context:
            D: DFA = parse_dfa(grammar)
        self.assertTrue('is not total' in str(context.exception))

        grammar = '''
            initial q0
            final q1
            input_symbols a b
            states q0 q1
            q0 q0 a
            q0 q1 b
            q1 q0 a
        '''
        with self.assertRaises(RuntimeError) as context:
            D: DFA = parse_dfa(grammar)
        self.assertTrue('is not total' in str(context.exception))


    def test_dfa_accepts_word(self):
        # accepts words ending in b
        grammar = '''
            S = aS + bT
            T = aS + bT + 1
        '''
        D: DFA = parse_dfa_baeten(grammar)
        self.assertTrue(dfa_accepts_word(D, 'abab'))
        self.assertFalse(dfa_accepts_word(D, 'abaa'))


    def test_dfa_simulate_word(self):
        grammar = '''
            S = aS + bT
            T = aS + bT + 1
        '''
        D: DFA = parse_dfa_baeten(grammar)
        result = [s[0] for s in dfa_simulate_word(D, 'abab')]
        expected_result = [State('S'), State('S'), State('T'), State('S'), State('T')]
        self.assertEqual(expected_result, result)


    def test_dfa_words_up_to_n(self):
        # accepts words ending in b
        grammar = '''
            S = aS + bT
            T = aS + bT + 1
        '''
        D: DFA = parse_dfa_baeten(grammar)
        words = dfa_words_up_to_n(D, 3)
        self.assertEqual(words, {'b', 'ab', 'bb', 'aab', 'abb', 'bab', 'bbb'})

    def _dfa_to_regexp_test(self, dfa_grammar: str, expected_result: str):
        D: DFA = parse_dfa_baeten(dfa_grammar)
        r: Regexp = dfa_to_regexp(D)
        result = str(r)
        self.assertEqual(result, expected_result)

    def test_dfa_to_regexp(self):
        grammar = '''
            S = 1
        '''
        self._dfa_to_regexp_test(grammar, '1')

        grammar = '''
            S = aT
            T = aU + 1
            U = aU
        '''
        self._dfa_to_regexp_test(grammar, 'a')

        grammar = '''
            S = aS + 1
        '''
        self._dfa_to_regexp_test(grammar, 'a*')

    def test_dfa_to_regexp_to_nfa(self):
        for i in range(100):
            print('test_dfa_to_regexp_to_nfa {}'.format(i))
            D = random_dfa({Symbol('a'), Symbol('b')}, 4)
            r = dfa_to_regexp(D)
            N = regexp_to_nfa(r)
            n = 4
            wordsD = dfa_words_up_to_n(D, n)
            wordsR = regexp_words_up_to_n(r, n)
            wordsN = nfa_words_up_to_n(N, n)
            if wordsD != wordsN or wordsD != wordsR:
                print('--- dfa ---')
                print(D)
                print('--- regexp ---')
                print(r)
                print('--- nfa ---')
                print(N)
                print('words_up_to_n(D, {}) = {}'.format(n, print_words(wordsD)))
                print('words_up_to_n(r, {}) = {}'.format(n, print_words(wordsR)))
                print('words_up_to_n(N, {}) = {}'.format(n, print_words(wordsN)))
            self.assertEqual(wordsD, wordsN, wordsR)

    def _test_dfa_minimize(self, D: DFA, minimize):
        D1 = minimize(D)
        n = 4
        wordsD = dfa_words_up_to_n(D, n)
        wordsD1 = dfa_words_up_to_n(D1, n)
        if wordsD != wordsD1:
            print('--- dfa D ---')
            print(D)
            print(f'--- dfa D1 ({minimize.__name__}) ---')
            print(D1)
            print('words_up_to_n(D, {}) = {}'.format(n, print_words(wordsD)))
            print('words_up_to_n(D1, {}) = {}'.format(n, print_words(wordsD1)))
            dot = draw_dfa(D.Q, D.Sigma, D.delta, D.q0, D.F)
            dot.render('D', format='png', view=True)
            dot = draw_dfa(D1.Q, D1.Sigma, D1.delta, D1.q0, D1.F)
            dot.render(f'{minimize.__name__}(D)', format='png', view=True)
        self.assertEqual(wordsD, wordsD1)
        self.assertLessEqual(len(D1.Q), len(D.Q))

    def test_dfa_minimize1(self):
        grammar = '''
            initial q0
            final q0 q1
            states q0 q1 q2
            q0 q1 a
            q0 q2 b
            q1 q2 a
            q1 q2 b
            q2 q2 a
            q2 q2 b
        '''
        D: DFA = parse_dfa(grammar)
        self._test_dfa_minimize(D, dfa_hopfcroft)
        self._test_dfa_minimize(D, dfa_quotient)

    def test_dfa_minimize2(self):
        # GambaTools.enable_logging = True
        for i in range(1000):
            D = random_dfa({Symbol('a'), Symbol('b')}, 5)
            self._test_dfa_minimize(D, dfa_quotient)
            self._test_dfa_minimize(D, dfa_hopfcroft)

    def test_dfa_isomorphic(self):
        for i in range(100):
            print('test_dfa_isomorphic {}'.format(i))
            D1 = random_dfa({Symbol('a'), Symbol('b')}, 5)
            D2 = permute_dfa_states(D1)
            self.assertTrue(dfa_isomorphic1(D1, D2))


def parse_dfa_baeten(text: str, check_validity: bool = True) -> DFA:
    G = parse_cfg_baeten(text)
    return cfg_to_dfa(G, check_validity)


if __name__ == '__main__':
    import unittest
    unittest.main()
