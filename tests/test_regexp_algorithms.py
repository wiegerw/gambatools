#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase

from gambatools.regexp import *
from gambatools.regexp_parser import parse_regexp
from gambatools.regexp_simple_parser import parse_simple_regexp
from gambatools.regexp_algorithms import regexp_symbols, regexp_to_nfa, regexp_simplify, regexp_accepts_word, \
    regexp_words_up_to_n, random_regexp, regexp_size
from gambatools.nfa_algorithms import nfa_words_up_to_n
from gambatools.printing import print_words


class Test(TestCase):
    def _regexp_symbols_test(self, text: str, expected_result: str):
        x = parse_regexp(text)
        symbols = set([symbol.symbol for symbol in regexp_symbols(x)])
        result = print_words(symbols)
        self.assertEqual(expected_result, result)

    def test_regexp_symbols(self):
        self._regexp_symbols_test('(a* + b)** + b + c*', '{a, b, c}')
        self._regexp_symbols_test('(a* + (b.c.d)*)*.e + b + c*', '{a, b, c, d, e}')

    def _print_regexp_test(self, x: Regexp, expected_result: str):
        result = str(x)
        self.assertEqual(expected_result, result)

    def test_print(self):
        self._print_regexp_test(Zero(), '0')
        self._print_regexp_test(One(), '1')
        self._print_regexp_test(Sum(One(), Zero()), '1 + 0')
        self._print_regexp_test(Iteration(Sum(One(), Zero())), '(1 + 0)*')

    def _parse_test(self, text: str, expected_result: str = None):
        if not expected_result:
            expected_result = text
        x = parse_regexp(text)
        result = str(x)
        self.assertEqual(expected_result, result)

    def _parse_simple_test(self, text: str, expected_result: str = None):
        if not expected_result:
            expected_result = text
        x = parse_simple_regexp(text)
        result = str(x)
        self.assertEqual(expected_result, result)

    def test_parse(self):
        self._parse_test('0')
        self._parse_test('0 + 1')
        self._parse_test('a')
        self._parse_test('a* + b')
        self._parse_test('(a* + b)** + b + a*')
        self._parse_test('a . b . c')
        self._parse_simple_test('a')
        self._parse_simple_test('a*bc', 'a* . b . c')
        self._parse_simple_test('a*bc*', 'a* . b . c*')
        self._parse_simple_test('abc', 'a . b . c')

    def _regexp_to_nfa_test(self, text: str, expected_result: str):
        # print('---------------')
        # print('text =', text)
        x = parse_simple_regexp(text)
        print('regexp_to_nfa_test x =', x)
        N = regexp_to_nfa(x)
        # print(N)
        wordsN = nfa_words_up_to_n(N, 3)
        result = print_words(wordsN)
        self.assertEqual(expected_result, result)

    def test_regexp_to_nfa(self):
        self._regexp_to_nfa_test('0', '{}')
        self._regexp_to_nfa_test('1', '{ε}')
        self._regexp_to_nfa_test('a', '{a}')
        self._regexp_to_nfa_test('a+b', '{a, b}')
        self._regexp_to_nfa_test('ab', '{ab}')
        self._regexp_to_nfa_test('abc', '{abc}')
        self._regexp_to_nfa_test('(a+b)c', '{ac, bc}')
        self._regexp_to_nfa_test('(a+b)(c+d)', '{ac, ad, bc, bd}')
        self._regexp_to_nfa_test('a*', '{ε, a, aa, aaa}')
        self._regexp_to_nfa_test('a**', '{ε, a, aa, aaa}')
        self._regexp_to_nfa_test('a*b', '{b, ab, aab}')
        self._regexp_to_nfa_test('(a+b)*', '{ε, a, b, aa, ab, ba, bb, aaa, aab, aba, abb, baa, bab, bba, bbb}')
        self._regexp_to_nfa_test('(a+b)*b', '{b, ab, bb, aab, abb, bab, bbb}')
        self._regexp_to_nfa_test('b(a+b)*', '{b, ba, bb, baa, bab, bba, bbb}')
        self._regexp_to_nfa_test('(a+b)*(a+b)*', '{ε, a, b, aa, ab, ba, bb, aaa, aab, aba, abb, baa, bab, bba, bbb}')
        self._regexp_to_nfa_test('a*b*', '{ε, a, b, aa, ab, bb, aaa, aab, abb, bbb}')
        self._regexp_to_nfa_test('a*cb*', '{c, ac, cb, aac, acb, cbb}')
        self._regexp_to_nfa_test('a*b(a+b)*', '{b, ab, ba, bb, aab, aba, abb, baa, bab, bba, bbb}')
        self._regexp_to_nfa_test('(a+b)*b(a+b)*', '{b, ab, ba, bb, aab, aba, abb, baa, bab, bba, bbb}')

    def _regex_simplify_test(self, text: str, expected_result: str):
        x = parse_regexp(text)
        result = str(regexp_simplify(x))
        self.assertEqual(expected_result, result)

    def test_regexp_simplify(self):
        self._regex_simplify_test('b . 0*', 'b')
        self._regex_simplify_test('0* . b', 'b')
        self._regex_simplify_test('b . 0* . b', 'b . b')

    def _regexp_accepts_word_test(self, text: str, w: str, expected_result: bool):
        x = parse_simple_regexp(text)
        result = regexp_accepts_word(x, w)
        self.assertEqual(expected_result, result)

    def test_regexp_accepts_word(self):
        self._regexp_accepts_word_test('0', '', False)
        self._regexp_accepts_word_test('1', '', True)
        self._regexp_accepts_word_test('a', 'a', True)
        self._regexp_accepts_word_test('a', 'b', False)
        self._regexp_accepts_word_test('a + b', 'a', True)
        self._regexp_accepts_word_test('a + b', 'b', True)
        self._regexp_accepts_word_test('a + b', 'ab', False)
        self._regexp_accepts_word_test('a + b', 'c', False)
        self._regexp_accepts_word_test('(a + b)(a + b)', 'aa', True)
        self._regexp_accepts_word_test('(a + b)(a + b)', 'ba', True)
        self._regexp_accepts_word_test('a*', '', True)
        self._regexp_accepts_word_test('a*', 'a', True)
        self._regexp_accepts_word_test('(a + b)*', '', True)
        self._regexp_accepts_word_test('(a + b)*', 'a', True)
        self._regexp_accepts_word_test('(a + b)*b(a + b)', 'aaba', True)
        self._regexp_accepts_word_test('(a + b)*b(a + b)', 'aaaa', False)

    def _regexp_words_up_to_n_test(self, text: str, n: int, expected_result: str):
        x = parse_simple_regexp(text)
        result = print_words(regexp_words_up_to_n(x, n))
        # print('L({}, {}) = {}'.format(x, n, result))
        self.assertEqual(expected_result, result)

    def test_regexp_words_up_to_n(self):
        self._regexp_words_up_to_n_test('0', 4, '{}')
        self._regexp_words_up_to_n_test('1', 4, '{ε}')
        self._regexp_words_up_to_n_test('a', 4, '{a}')
        self._regexp_words_up_to_n_test('a + b', 4, '{a, b}')
        self._regexp_words_up_to_n_test('(a + b)(a + b)', 2, '{aa, ab, ba, bb}')
        self._regexp_words_up_to_n_test('a*', 0, '{ε}')
        self._regexp_words_up_to_n_test('a*', 1, '{ε, a}')
        self._regexp_words_up_to_n_test('a*', 2, '{ε, a, aa}')
        self._regexp_words_up_to_n_test('(a + b)*b(a + b)*', 3, '{b, ab, ba, bb, aab, aba, abb, baa, bab, bba, bbb}')

    def _random_regexp_test(self, n: int):
        from gambatools import dfa

        Sigma = {dfa.Symbol('a'), dfa.Symbol('b')}
        expected_result = n

        x = random_regexp(Sigma, n)
        print('random_regexp({}, {}) = {}'.format(print_words(Sigma), n, x))
        result = regexp_size(x)
        self.assertEqual(expected_result, result)


    def test_random_regexp(self):
        for i in range(10):
            self._random_regexp_test(4)
        for i in range(10):
            self._random_regexp_test(10)

    def test_regexp_to_nfa_random(self):
        from gambatools import dfa
        a = dfa.Symbol('a')
        b = dfa.Symbol('b')
        for i in range(100):
            print('test_regexp_to_nfa_random {}'.format(i))
            r = random_regexp({a, b}, 4)
            N = regexp_to_nfa(r)
            n = 4
            wordsR = regexp_words_up_to_n(r, n)
            wordsN = nfa_words_up_to_n(N, n)
            if wordsR != wordsN:
                print('r =', r)
                print(N)
                print('words_up_to_n(r, {}) = {}'.format(n, print_words(wordsR)))
                print('words_up_to_n(N, {}) = {}'.format(n, print_words(wordsN)))
            self.assertEqual(wordsR, wordsN)


if __name__ == '__main__':
    import unittest
    unittest.main()
