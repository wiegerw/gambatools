#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase

from gambatools.tm_algorithms import tm_accepts_word, tm_words_up_to_n, tm_simulate_word, print_tm_state, parse_tm
from gambatools.printing import print_words


class Test(TestCase):
    def test_tm1(self):
        tm = '''
            % Sipser 3rd edition figure 3.8
            initial q1
            accept q_accept
            reject q_reject
            input_symbols 0
            tape_symbols 0 x _
            blank _
            q1 q2 0_,R
            q1 q_reject __,R xx,R
            q2 q2 xx,R
            q2 q3 0x,R
            q2 q_accept __,R
            q3 q3 xx,R
            q3 q4 00,R
            q3 q5 __,L
            q4 q3 0x,R
            q4 q4 xx,R
            q4 q_reject __,R
            q5 q2 __,R
            q5 q5 00,L xx,L
        '''
        T = parse_tm(tm)
        self.assertTrue(tm_accepts_word(T, '0000'))

        result = print_words(tm_words_up_to_n(T, 8))
        expected_result = '{0, 00, 0000, 00000000}'
        self.assertEqual(expected_result, result)

        states = tm_simulate_word(T, '0000')
        print('execution of input "0000"')
        for q, tape, head in states:
            print_tm_state(q, tape, head)

    def test_tm2(self):
        tm = '''
            % Sipser 3rd edition figure 3.10
            initial q1
            accept q_accept
            input_symbols 0 1 #
            tape_symbols 0 1 # x _
            q1 q2 0x,R
            q1 q3 1x,R
            q1 q8 ##,R
            q2 q2 00,R 11,R
            q2 q4 ##,R
            q3 q3 00,R 11,R
            q3 q5 ##,R
            q4 q4 xx,R
            q4 q6 0x,L
            q5 q5 xx,R
            q5 q6 1x,L
            q6 q6 00,L 11,L xx,L
            q6 q7 ##,L
            q7 q7 00,L 11,L
            q7 q1 xx,R
            q8 q8 xx,R
            q8 q_accept __,R
        '''
        T = parse_tm(tm)
        self.assertTrue(tm_accepts_word(T, '0#0'))
        self.assertTrue(tm_accepts_word(T, '1011#1011'))

        result = print_words(tm_words_up_to_n(T, 5))
        expected_result = '{#, 0#0, 1#1, 00#00, 01#01, 10#10, 11#11}'
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    import unittest
    unittest.main()
