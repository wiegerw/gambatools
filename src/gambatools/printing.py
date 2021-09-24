#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Iterable


def header(msg):
    print('-------------------')
    print('--- {}'.format(msg))
    print('-------------------')


def print_words(words: Iterable[str], epsilon='ε', separator=', ', leftsep='{', rightsep='}') -> str:
    words = sorted([w if w not in ['', epsilon] else 'ε' for w in words])
    return '{}{}{}'.format(leftsep, separator.join(sorted(words, key=lambda x: (len(x), x if x != 'ε' else ''))), rightsep)
