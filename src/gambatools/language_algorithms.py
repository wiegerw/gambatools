#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Set
import itertools


def intersection(L1: Set[str], L2: Set[str]) -> Set[str]:
    """Returns the intersection of L1 and L2"""
    return L1 & L2


def union(L1: Set[str], L2: Set[str]) -> Set[str]:
    """Returns the union of L1 and L2"""
    return L1 | L2


def symmetric_difference(L1: Set[str], L2: Set[str]) -> Set[str]:
    """Returns the symmetric difference of L1 and L2"""
    return L1 ^ L2


def concatenation(L1: Set[str], L2: Set[str]) -> Set[str]:
    """Returns the concatenation of L1 and L2"""
    return set(w1 + w2 for (w1, w2) in itertools.product(L1, L2))


def language_reverse(L: Set[str]) -> Set[str]:
    """Returns the reverse of L"""
    return set(w[::-1] for w in L)


def words_of_length_n(Sigma: Set[str], n: int) -> Set[str]:
    """Returns all words w in Sigma^* with length n"""
    return set(''.join(x) for x in itertools.product(Sigma, repeat=n))


def words_up_to_n(Sigma: Set[str], n: int) -> Set[str]:
    """Returns all words w in Sigma^* with length <= n"""
    return set().union(*[words_of_length_n(Sigma, i) for i in range(n+1)])


def language_no_prefix(L: Set[str]) -> Set[str]:
    """Returns all words w in L such that no proper prefix of w is in L"""

    def has_prefix_in_L(w: str) -> bool:
        return any(w[i:] in L for i in range(1, len(w)))

    return set(w for w in L if not has_prefix_in_L(w))


def language_no_extend(L: Set[str]) -> Set[str]:
    """Returns all words w in L such that w is not a proper prefix of any word in L"""

    def is_proper_prefix(v: str, w: str) -> bool:
        return w.startswith(v) and w != v

    return set(w for w in L if all(not is_proper_prefix(w, v) for v in L))


# def words_up_to_n(Sigma: Set[str], n: int) -> Set[str]:
#     """Returns all words w in Sigma^* with length at most n"""
#     return set().union(*words_up_to_n(Sigma, k) for k in range(n + 1))


def parse_word_list(word_list: str) -> Set[str]:
    words = [word.strip() for word in word_list.strip().split()]
    words = ['' if word in ['ε', '_'] else word for word in words]
    return set(words)
