#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List


def first_index(x: List, value) -> int:
    return x.index(value)


def last_index(x: List, value) -> int:
    return len(x) - list(reversed(x)).index(value) - 1
