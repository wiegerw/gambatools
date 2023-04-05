#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from unittest import TestCase
import copy

from gambatools.language_algorithms import words_up_to_n
from gambatools.pda_algorithms import pda_accepts_word, pda_words_up_to_n, pda_to_cfg, \
    pda_to_push_pop, pda_to_one_accepting_state_in_place, print_pda, pda_is_push_pop, parse_pda
from gambatools.pda import PDA
from gambatools.cfg_algorithms import cfg_words_up_to_n, cfg_remove_inproductive_variables_in_place, \
    cfg_remove_epsilon_rules_in_place, cfg_remove_useless_rules_in_place
from gambatools.printing import print_words
from gambatools.text_utility import read_utf8_text, remove_comments


class Test(TestCase):
    def _pda_to_push_pop_test(self, P: PDA):
        P1 = pda_to_push_pop(P)
        n = 4
        wordsP = pda_words_up_to_n(P, n)
        wordsP1 = pda_words_up_to_n(P1, n)
        if wordsP != wordsP1:
            print('--- P ---\n{}'.format(print_pda(P)))
            print('--- P1 ---\n{}'.format(print_pda(P1)))
        self.assertEqual(print_words(wordsP), print_words(wordsP1))

    def _pda_to_one_accepting_state_test(self, P: PDA):
        P1 = copy.deepcopy(P)
        pda_to_one_accepting_state_in_place(P1)
        n = 4
        wordsP = pda_words_up_to_n(P, n)
        wordsP1 = pda_words_up_to_n(P1, n)
        if wordsP != wordsP1:
            print('--- P ---\n{}'.format(print_pda(P)))
            print('--- P1 ---\n{}'.format(print_pda(P1)))
        self.assertEqual(print_words(wordsP), print_words(wordsP1))

    def _pda_to_cfg_test(self, P: PDA, accepts_on_empty_stack: bool = False):
        n = 4
        wordsP = pda_words_up_to_n(P, n)
        G = pda_to_cfg(P, accepts_on_empty_stack)
        print('--- G ---\n{}'.format(G))
        print('start =', G.S)
        cfg_remove_epsilon_rules_in_place(G)
        print('--- G remove epsilon ---\n{}'.format(G))
        print('start =', G.S)
        cfg_remove_inproductive_variables_in_place(G)
        print('--- G remove inproductive ---\n{}'.format(G))
        print('start =', G.S)
        cfg_remove_useless_rules_in_place(G)
        print('--- G remove useless ---\n{}'.format(G))
        print('start =', G.S)
        wordsG = cfg_words_up_to_n(G, n)
        print('wordsP', print_words(wordsP))
        print('wordsG', print_words(wordsG))
        if wordsP != wordsG:
            print('--- P ---\n{}'.format(print_pda(P)))
            print('--- G ---\n{}'.format(G))
            print('start =', G.S)
        self.assertEqual(print_words(wordsP), print_words(wordsG))

    def test_pda0(self):
        # This PDA accepts on empty stack
        pda = '''
            % Sipser 3rd edition figure 2.15
            % language { 0^n 1^n | n >= 0 }
            initial q1
            final q1 q4
            states q1 q2 q3 q4
            input_symbols 0 1
            epsilon _
            q1 q2 _,_$
            q2 q2 0,_0
            q2 q3 1,0_
            q3 q3 1,0_
            q3 q4 _,$_
        '''
        P = parse_pda(pda)

        self.assertTrue(pda_accepts_word(P, '01'))
        self.assertTrue(pda_accepts_word(P, '0011'))
        self.assertFalse(pda_accepts_word(P, '0'))

        words = pda_words_up_to_n(P, 4)
        result = print_words(words)
        expected_result = '{ε, 01, 0011}'
        self.assertEqual(expected_result, result)

        self._pda_to_one_accepting_state_test(P)
        self._pda_to_push_pop_test(P)
        self._pda_to_cfg_test(P, True)
        self._pda_to_cfg_test(P, False)

    def test_pda1(self):
        # This PDA accepts on empty stack
        pda = '''
            % Sipser 3rd edition figure 2.19
            % language { w w^R | w in {a,b}* }
            initial q1
            final q4
            epsilon _
            q1 q2 _,_$
            q2 q2 0,_0 1,_1
            q2 q3 _,__
            q3 q3 0,0_ 1,1_
            q3 q4 _,$_
        '''
        P = parse_pda(pda)

        self.assertTrue(pda_accepts_word(P, '00'))
        self.assertTrue(pda_accepts_word(P, '0110'))
        self.assertFalse(pda_accepts_word(P, '0'))

        result = print_words(pda_words_up_to_n(P, 4))
        expected_result = '{ε, 00, 11, 0000, 0110, 1001, 1111}'
        self.assertEqual(result, expected_result)

        self._pda_to_one_accepting_state_test(P)
        self._pda_to_push_pop_test(P)
        self._pda_to_cfg_test(P, True)
        self._pda_to_cfg_test(P, False)

    def test_pda2(self):
        # This PDA accepts on empty stack
        pda = '''
            % language #_a(w) = 2#_b(w)
            initial q0
            final q6
            q0 q1 _,_$
            q1 q2 _,$$
            q1 q3 _,$$
            q1 q6 _,$_
            q2 q1 _,$$
            q2 q2 a,n_
            q2 q5 b,_n
            q3 q1 _,$$
            q3 q3 a,_p
            q3 q4 b,p_
            q4 q3 _,p_
            q4 q5 _,$$
            q5 q2 _,_n
        '''
        P = parse_pda(pda)

        self.assertTrue(pda_accepts_word(P, 'aab'))
        self.assertTrue(pda_accepts_word(P, 'aba'))
        self.assertTrue(pda_accepts_word(P, 'baa'))
        self.assertTrue(pda_accepts_word(P, 'baaaba'))
        self.assertFalse(pda_accepts_word(P, 'a'))
        self.assertFalse(pda_accepts_word(P, 'bababa'))

        result = print_words(pda_words_up_to_n(P, 6))
        expected_result = '{ε, aab, aba, baa, aaaabb, aaabab, aaabba, aabaab, aababa, aabbaa, abaaab, abaaba, ababaa, abbaaa, baaaab, baaaba, baabaa, babaaa, bbaaaa}'
        self.assertEqual(result, expected_result)

        self._pda_to_one_accepting_state_test(P)
        self._pda_to_push_pop_test(P)
        # self.pda_to_cfg_test(P) # does not finish!

    def test_pda_to_cfg(self):
        pda = '''
            initial A
            final C
            A B a,_$
            B C b,$_
        '''
        P = parse_pda(pda)
        self.assertTrue(pda_is_push_pop(P))
        self._pda_to_one_accepting_state_test(P)
        self._pda_to_push_pop_test(P)
        self._pda_to_cfg_test(P, True)
        self._pda_to_cfg_test(P, False)

        pda = '''
            initial A
            final C
            A B _,_$
            B B a,_0 b,0_
            B C _,$_
        '''
        P = parse_pda(pda)
        self.assertTrue(pda_is_push_pop(P))
        self._pda_to_one_accepting_state_test(P)
        self._pda_to_push_pop_test(P)
        self._pda_to_cfg_test(P, True)
        self._pda_to_cfg_test(P, False)

        pda = '''
            initial A
            final C
            A B _,_$
            B C _,$_
        '''
        P = parse_pda(pda)
        self.assertTrue(pda_is_push_pop(P))
        self._pda_to_one_accepting_state_test(P)
        self._pda_to_push_pop_test(P)
        self._pda_to_cfg_test(P, True)
        self._pda_to_cfg_test(P, False)

    def test_epsilon(self):
        pda = '''
            initial q0
            final q1
            q0 q1 _,_$
        '''
        P = parse_pda(pda)

        pda = '''
            epsilon _
            initial q0
            final q1
            q0 q1 _,_$
        '''
        P = parse_pda(pda)

        pda = '''
            initial q0
            final q1
            q0 q1 ε,ε$
        '''
        P = parse_pda(pda)

        pda = '''
            epsilon ε
            initial q0
            final q1
            q0 q1 ε,ε$
        '''
        P = parse_pda(pda)

    def test_pda_words_up_to_n(self):
        count = 0
        length = 8
        if not os.path.exists('../examples/pda'):
            return
        for filename in sorted(os.listdir('../examples/pda')):
            if not filename.endswith('.pda'):
                continue
            count = count + 1
            text = read_utf8_text(os.path.join('../examples/pda', filename))
            P = parse_pda(text)
            all_words = words_up_to_n(P.Sigma, length)
            words = pda_words_up_to_n(P, length)
            self.assertTrue(all(len(word) <= length for word in words))
            print(filename, len(words))
            for word in all_words:
                if not pda_accepts_word(P, word) == (word in words):
                    print('word =', word)
                    print(remove_comments(text))
                self.assertTrue(pda_accepts_word(P, word) == (word in words))
        self.assertGreater(count, 0)


if __name__ == '__main__':
    import unittest
    unittest.main()
