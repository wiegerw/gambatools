#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest import TestCase

from gambatools.language_algorithms import words_of_length_n, words_up_to_n


class Test(TestCase):
    def test_words_of_length_n(self):
        words = words_of_length_n({'a', 'b'}, 3)
        self.assertEqual(words, {'aaa', 'aab', 'aba', 'abb', 'baa', 'bab', 'bba', 'bbb'})

    def test_words_up_to_n(self):
        words = words_up_to_n({'a', 'b'}, 3)
        self.assertEqual(words, {'', 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa', 'aab', 'aba', 'abb', 'baa', 'bab', 'bba', 'bbb'})


if __name__ == '__main__':
    import unittest
    unittest.main()
