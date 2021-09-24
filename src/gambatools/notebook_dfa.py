#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List, Tuple

from gambatools.automaton_algorithms import state_product_regex
from gambatools.dfa_algorithms import parse_dfa, dfa_union, dfa_intersection, dfa_symmetric_difference, \
    dfa_complement, dfa_words_up_to_n
from gambatools.dfa import DFA, State, Symbol
from gambatools.language_algorithms import language_reverse
from gambatools.language_generator import compare_languages, check_equal_languages, generate_language
from gambatools.nfa_algorithms import parse_nfa
from gambatools.notebook import print_feedback, show, show_product


def extract_states(q: State) -> Tuple[State, State]:
    labels = q[1:-1].split(',')
    return State(labels[0]), State(labels[1])


def check_product_automaton(D: DFA, D1: DFA, D2: DFA, answer: DFA) -> List[str]:
    feedback = []

    # check if the states in answer are proper product states
    for q in answer.Q:
        q1, q2 = extract_states(q)
        if q1 not in D1.Q or q2 not in D2.Q:
            feedback.append('The state {} is not a valid product state'.format(q))

    if D.Sigma != answer.Sigma:
        feedback.append('The alphabet of the complement should be equal to the alphabet of the original DFA')

    # check the initial state
    if answer.q0 != D.q0:
        feedback.append('The initial state should be {}'.format(D.q0))

    # check the transitions
    for (q, a), q1 in answer.delta.items():
        if (q, a) in D.delta and q1 != D.delta[q, a]:
            feedback.append('The {}-transition from {} should have target {}'.format(a, q, q1))

    # check the final states
    for q in D.F - answer.F:
        feedback.append('The state {} should be final'.format(q))
    for q in answer.F - D.F:
        feedback.append('The state {} should not be final'.format(q))

    return feedback


def check_dfa_union(dfa: str, dfa1: str, dfa2: str, length: int = 8) -> None:
    from gambatools.language_algorithms import union
    try:
        D1 = parse_dfa(dfa1)
        D2 = parse_dfa(dfa2)
        D = dfa_union(D1, D2)
        answer = parse_dfa(dfa, state_regex=state_product_regex())
        feedback = check_product_automaton(D, D1, D2, answer)
        L1 = dfa_words_up_to_n(D1, length)
        L2 = dfa_words_up_to_n(D2, length)
        L = dfa_words_up_to_n(answer, length)
        feedback = feedback + compare_languages(L, union(L1, L2))
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))


def check_dfa_intersection(dfa: str, dfa1: str, dfa2: str, length: int = 8) -> None:
    from gambatools.language_algorithms import intersection
    try:
        D1 = parse_dfa(dfa1)
        D2 = parse_dfa(dfa2)
        D = dfa_intersection(D1, D2)
        answer = parse_dfa(dfa, state_regex=state_product_regex())
        feedback = check_product_automaton(D, D1, D2, answer)
        L1 = dfa_words_up_to_n(D1, length)
        L2 = dfa_words_up_to_n(D2, length)
        L = dfa_words_up_to_n(answer, length)
        feedback = feedback + compare_languages(L, intersection(L1, L2))
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))


def check_dfa_symmetric_difference(dfa: str, dfa1: str, dfa2: str, length: int = 8) -> None:
    from gambatools.language_algorithms import symmetric_difference
    try:
        D1 = parse_dfa(dfa1)
        D2 = parse_dfa(dfa2)
        D = dfa_symmetric_difference(D1, D2)
        answer = parse_dfa(dfa, state_regex=state_product_regex())
        feedback = check_product_automaton(D, D1, D2, answer)
        L1 = dfa_words_up_to_n(D1, length)
        L2 = dfa_words_up_to_n(D2, length)
        L = dfa_words_up_to_n(answer, length)
        feedback = feedback + compare_languages(L, symmetric_difference(L1, L2))
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))


def check_dfa_complement(dfa: str, dfa1: str, length: int = 8) -> None:
    try:
        D1 = parse_dfa(dfa1)
        D = dfa_complement(D1)
        answer = parse_dfa(dfa)

        feedback = []

        if D.Sigma != answer.Sigma:
            feedback.append('The alphabet of the complement should be equal to the alphabet of the original DFA')

        if D.Q != answer.Q:
            feedback.append('The states of the complement should be equal to the states of the original DFA')

        if D.q0 != answer.q0:
            feedback.append('The initial state of the complement should be equal to the initial state of the original DFA')

        if D.delta != answer.delta:
            feedback.append('The transitions of the complement should be equal to the transitions of the original DFA')

        # check the final states
        for q in D.F - answer.F:
            feedback.append('The state {} should be final'.format(q))
        for q in answer.F - D.F:
            feedback.append('The state {} should not be final'.format(q))

        feedback = []
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))


def check_dfa_reverse(dfa: str, nfa: str, length: int = 8) -> None:
    try:
        D = parse_dfa(dfa)
        answer = parse_nfa(nfa)

        feedback = []

        if D.Sigma != answer.Sigma:
            feedback.append('Error: the alphabet of the complement should be equal to the alphabet of the original DFA')

        if not D.Q <= answer.Q:
            feedback.append('Warning: the states of the original DFA should be reused')

        for (q, a), q1 in D.delta.items():
            if q not in answer.delta[q1, a]:
                feedback.append('Warning: the reversed transition {} --{}-> {} is missing'.format(q1, a, q))
                break

        if answer.q0 in D.Q:
            feedback.append('Warning: a new initial state should be introduced')

        if answer.F != {D.q0}:
            feedback.append('Warning: the initial state of the DFA should be the final state of the NFA')

        L1 = generate_language(answer, length)
        L2 = language_reverse(generate_language(D, length))
        feedback = feedback + compare_languages(L1, L2)

        print_feedback(feedback)

    except Exception as e:
        print('Error: {}'.format(e))


