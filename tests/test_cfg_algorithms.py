#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from unittest import TestCase

from gambatools.cfg import CFG, Alternative, Variable, cfg_equal_alternatives
from gambatools.cfg_algorithms import parse_cfg_baeten, expand_nullable_variables, BaetenCFGParser, \
    cfg_remove_epsilon_rules, cfg_eliminate_unit_rules, cfg_add_new_start_variable, cfg_make_rules_of_length_two, \
    cfg_to_chomsky, cfg_words_up_to_n, cfg_accepts_word, parse_simple_cfg, \
    cfg_add_new_start_variable_in_place, cfg_remove_epsilon_rules_in_place, cfg_eliminate_unit_rules_in_place, \
    cfg_make_rules_of_length_two_in_place, cfg_eliminate_terminals_in_place, \
    cfg_derivable_variables, cfg_print_simple, cfg_is_simple

from gambatools.cfg_parser import parse_cfg
from gambatools.language_algorithms import words_of_length_n, words_up_to_n
from gambatools.printing import print_words
from gambatools.text_utility import read_utf8_text, remove_comments


def parse_cfg_alternative(text: str) -> Alternative:
    parser = BaetenCFGParser()
    return parser.parse_alternative(text)


class Test(TestCase):
    def test_expand_nullable_variables(self):
        grammar = '''
            S = aS + bT
            T = aS + bT + aTU + 1
            U = bU + 1
        '''
        G: CFG = parse_cfg_baeten(grammar)
        R = G.R
        W = set([rule.variable for rule in R if rule.is_epsilon()])
        self.assertEqual(W, {Variable('T'), Variable('U')})

        x = parse_cfg_alternative('aSbTU')
        y = [Alternative(symbols) for symbols in expand_nullable_variables(x.symbols, W)]

        y0 = parse_cfg_alternative('aSb')
        y1 = parse_cfg_alternative('aSbT')
        y2 = parse_cfg_alternative('aSbU')
        y3 = parse_cfg_alternative('aSbTU')

        self.assertTrue(cfg_equal_alternatives(y, [y0, y1, y2, y3]))

    def test_cfg_eliminate_epsilon_rules(self):
        grammar = '''
            S = aS + aT + bT + 1
            T = cS + S + bT + aTU + 1
            U = bU + 1
        '''
        G: CFG = parse_cfg_baeten(grammar)
        G1 = cfg_remove_epsilon_rules(G)

        expected_result = '''
            S = aS + aT + bT + a + b + 1
            T = cS + S + bT + b + aTU + aT + aU + a + c
            U = bU + b
        '''
        G2: CFG = parse_cfg_baeten(expected_result)
        self.assertEqual(G1, G2)

    def test_cfg_eliminate_unit_rules(self):
        grammar = '''
            S -> Aa | B
            A -> b | B
            B -> A | a
        '''
        G: CFG = parse_simple_cfg(grammar)
        G1 = cfg_eliminate_unit_rules(G)
        expected_result = '''
            S -> Aa | b | a
            A -> b | a
            B -> a | b
        '''
        G2: CFG = parse_simple_cfg(expected_result)
        self.assertEqual(G1, G2)

    def test_cfg_add_new_start_variable_in_place(self):
        grammar = '''
            S = aS + bT
            T = aS + bT + 1
        '''
        G: CFG = parse_cfg_baeten(grammar)
        G1 = cfg_add_new_start_variable(G, 'R')
        expected_result = '''
            R = S
            S = aS + bT
            T = aS + bT + 1
        '''
        G2: CFG = parse_cfg_baeten(expected_result)
        self.assertEqual(G1, G2)

    def test_cfg_make_rules_of_length_two(self):
        grammar = '''
            S -> aTU | bT
            T -> aS | bT | ε
            U -> abST | ε
        '''
        G: CFG = parse_simple_cfg(grammar)
        G1 = cfg_make_rules_of_length_two(G)
        expected_result = '''
            S -> aA | bT
            T -> aS | bT | ε
            U -> aB | ε
            A -> TU
            B -> bC
            C -> ST
        '''
        G2: CFG = parse_simple_cfg(expected_result)
        self.assertEqual(G1, G2)

    def test_cfg_to_chomsky(self):
        grammar = '''
            S = aTU + bT
            T = aS + bT + 1
            U = abST + 1
        '''
        G: CFG = parse_cfg_baeten(grammar)
        G1 = cfg_to_chomsky(G)
        self.assertTrue(G1.is_chomsky())

    def test_cfg_words_up_to_n(self):
        count = 0
        length = 5
        if not os.path.exists('../examples/cfg'):
            return
        for filename in os.listdir('../examples/cfg'):
            if not filename.endswith('.cfg'):
                continue
            count = count + 1
            text = read_utf8_text(os.path.join('../examples/cfg', filename))
            G = parse_simple_cfg(text)
            all_words = words_up_to_n(G.Sigma, length)
            words = cfg_words_up_to_n(G, length)
            self.assertTrue(all(len(word) <= length for word in words))
            print(filename, len(words))
            for word in all_words:
                if not cfg_accepts_word(G, word) == (word in words):
                    print('word =', word)
                    print(remove_comments(text))
                self.assertTrue(cfg_accepts_word(G, word) == (word in words))
        self.assertGreater(count, 0)

    def test_cfg_accepts_word(self):
        grammar = '''
            S = AB + BC
            A = BA + a
            B = CC + b
            C = AB + a
        '''
        G: CFG = parse_cfg_baeten(grammar)
        self.assertTrue(G.is_chomsky())
        w = 'baaba'
        self.assertTrue(cfg_accepts_word(G, w))

        grammar = '''
            S -> a
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, 'a'))
        self.assertFalse(cfg_accepts_word(G, 'aa'))

        grammar = '''
            S -> a | b
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, 'a'))
        self.assertTrue(cfg_accepts_word(G, 'b'))
        self.assertFalse(cfg_accepts_word(G, 'aa'))

        grammar = '''
            S -> AS | b
            A -> a
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, 'b'))
        self.assertTrue(cfg_accepts_word(G, 'ab'))

        grammar = '''
            S -> AB
            A -> a
            B -> b
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, 'ab'))

        grammar = '''
            S -> AB
            A -> a
            T -> AB
            B -> b
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, 'ab'))

        grammar = '''
            S -> Ab
            A -> a
        '''
        G: CFG = parse_simple_cfg(grammar)
        G1: CFG = cfg_to_chomsky(G)
        self.assertTrue(cfg_accepts_word(G, 'ab'))

        grammar = '''
            S -> aS | b
        '''
        G: CFG = parse_simple_cfg(grammar)
        G1: CFG = cfg_to_chomsky(G)
        self.assertTrue(cfg_accepts_word(G, 'b'))
        self.assertTrue(cfg_accepts_word(G, 'ab'))

        grammar = '''
            S -> _
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, ''))

        grammar = '''
            S -> aSb | _
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, ''))
        self.assertTrue(cfg_accepts_word(G, 'ab'))

        grammar = '''
            S -> aSb | T
            T -> Bb | bb | aA | ab | a
            A -> aA | a
            B -> bB | b
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertTrue(cfg_accepts_word(G, 'bb'))

        grammar = '''
            S -> X | Y
            X -> AZ | ZA | XX
            Y -> BZ | ZB | YY
            Z -> aZb | bZa | ZZ | _
            A -> aA | a
            B -> bB | b
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertFalse(cfg_accepts_word(G, 'ab'))

    def test_parse_cfg(self):
        grammar = '''
            S -> A'.A' ;
            A' -> b.A' | a
        '''
        G: CFG = parse_cfg(grammar)
        S = Variable('S')
        A1 = Variable("A'")
        V = {S, A1}
        self.assertEqual(V, G.V)

    def test_parse_cfg_simple(self):
        grammar = '''
            S -> a
        '''
        G = parse_simple_cfg(grammar)

        grammar = '''
            S -> aS | _
        '''
        G = parse_simple_cfg(grammar)

        grammar = '''
            epsilon = e
            S -> AA | abc
            A -> bA | e
        '''
        G = parse_simple_cfg(grammar)

        grammar = '''
            S -> T | U
            T -> aTb | _
            U -> bUa | _
        '''
        G = parse_simple_cfg(grammar)


    def test_cfg_derivable_variables(self):
        def variables(V):
            return set([Variable(v) for v in V.split()])

        grammar = '''
            S -> Aa | B
            A -> b | B
            B -> A | a
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertEqual(cfg_derivable_variables(G, Variable('S')), variables('A B'))
        self.assertEqual(cfg_derivable_variables(G, Variable('A')), variables('B'))
        self.assertEqual(cfg_derivable_variables(G, Variable('B')), variables('A'))

        grammar = '''
            S -> A | b
            A -> A | B | a
            B -> S | c
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertEqual(cfg_derivable_variables(G, Variable('S')), variables('A B'))
        self.assertEqual(cfg_derivable_variables(G, Variable('A')), variables('B S'))
        self.assertEqual(cfg_derivable_variables(G, Variable('B')), variables('A S'))

        grammar = '''
            S_0 -> S
            S -> X | Y
            X -> AZ | A | ZA | XX
            Y -> BZ | B | ZB | YY
            Z -> aZb | ab | bZa | ba | ZZ | Z
            A -> aA | a
            B -> bB | b
        '''
        G: CFG = parse_simple_cfg(grammar)
        self.assertEqual(cfg_derivable_variables(G, Variable('A')), variables(''))
        self.assertEqual(cfg_derivable_variables(G, Variable('B')), variables(''))
        self.assertEqual(cfg_derivable_variables(G, Variable('X')), variables('A'))


if __name__ == '__main__':
    import unittest
    unittest.main()
