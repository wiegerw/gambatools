#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Set
from gambatools.automaton import Automaton
from gambatools.dfa_algorithms import dfa_words_up_to_n, automaton_to_dfa
from gambatools.nfa_algorithms import nfa_words_up_to_n, automaton_to_nfa


def _compare_words(accepted_words: Set[str], expected_words: Set[str]):
    if 'ε' in expected_words:
        expected_words.remove('ε')
        expected_words.add('')

    if accepted_words != expected_words:
        accepted_minus_expected = accepted_words - expected_words
        if len(accepted_minus_expected) > 0:
            word = next(iter(accepted_minus_expected))
            word = word if word else 'ε'
            feedback = "word '{}' should not be accepted".format(word)
        else:
            word = next(iter(expected_words - accepted_words))
            word = word if word else 'ε'
            feedback = "word '{}' is not accepted".format(word)
        return { 'correct': False, 'feedback': feedback }
    return {'correct': True}


def check_dfa_for_given_language(states, transitions, initial_states, final_states, language: str, max_word_length=5):
    try:
        D = automaton_to_dfa(Automaton(states, transitions, initial_states, final_states, {}))
        expected_words = set(language.split())
        accepted_words = dfa_words_up_to_n(D, max_word_length)
        return _compare_words(accepted_words, expected_words)
    except RuntimeError as e:
        return { 'correct': False, 'feedback': str(e) }

def check_nfa_for_given_language(states, transitions, initial_states, final_states, language: str, max_word_length=5):
    try:
        N = automaton_to_nfa(Automaton(states, transitions, initial_states, final_states, {}))
        expected_words = set(language.split())
        accepted_words = nfa_words_up_to_n(N, max_word_length)
        return _compare_words(accepted_words, expected_words)
    except RuntimeError as e:
        return { 'correct': False, 'feedback': str(e) }
