#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List


def remove_none(seq: List):
    return [x for x in seq if x]


def remove_duplicates(seq: List):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def remove_if(seq: List, predicate):
    index = len(seq) - 1
    while index >= 0:
        if predicate(seq[index]):
            del seq[index]
        index = index - 1
    return seq
