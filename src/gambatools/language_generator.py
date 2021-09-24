#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Set, List

import gambatools.dfa
import gambatools.dfa_algorithms
import gambatools.nfa
import gambatools.nfa_algorithms
import gambatools.pda
import gambatools.pda_algorithms
import gambatools.tm
import gambatools.tm_algorithms
import gambatools.cfg
import gambatools.cfg_algorithms
import gambatools.regexp
import gambatools.regexp_algorithms


def generate_language(L: Any, n: int) -> Set[str]:
    if isinstance(L, set) and all(isinstance(w, str) for w in L):
        result = L
    elif isinstance(L, gambatools.dfa.DFA):
        result = gambatools.dfa_algorithms.dfa_words_up_to_n(L, n)
    elif isinstance(L, gambatools.nfa.NFA):
        result = gambatools.nfa_algorithms.nfa_words_up_to_n(L, n)
    elif isinstance(L, gambatools.pda.PDA):
        result = gambatools.pda_algorithms.pda_words_up_to_n(L, n)
    elif isinstance(L, gambatools.tm.TM):
        result = gambatools.tm_algorithms.tm_words_up_to_n(L, n)
    elif isinstance(L, gambatools.cfg.CFG):
        result = gambatools.cfg_algorithms.cfg_words_up_to_n(L, n)
    elif isinstance(L, gambatools.regexp.Regexp):
        result = gambatools.regexp_algorithms.regexp_words_up_to_n(L, n)
    else:
        raise RuntimeError('cannot generate a language for type {}'.format(L.__class__))
    return result


# A1 is the user supplied answer
# A2 is the expected result
def compare_languages(A1: Set[str], A2: Set[str]) -> List[str]:
    A1minusA2 = sorted(A1 - A2, key=lambda x: (len(x)))
    A2minusA1 = sorted(A2 - A1, key=lambda x: (len(x)))
    feedback = []
    if len(A1minusA2) > 0:
        word = A1minusA2[0]
        word = 'ε' if not word else word
        feedback.append("Error: word '{}' should not be accepted".format(word))
    elif len(A2minusA1) > 0:
        word = A2minusA1[0]
        word = 'ε' if not word else word
        feedback.append("Error: word '{}' should be accepted".format(word))
    return feedback


# A1 is the user supplied answer
# A2 is the expected result
def check_equal_languages(L1: Any, L2: Any, length: int = 4) -> List[str]:
    A1 = generate_language(L1, length)
    A2 = generate_language(L2, length)
    return compare_languages(A1, A2)
