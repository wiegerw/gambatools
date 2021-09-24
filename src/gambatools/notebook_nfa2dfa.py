#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import itertools
import re
from typing import Set

from gambatools.automaton_algorithms import state_set_regex
from gambatools.dfa import DFA, State, print_state_set
from gambatools.dfa_algorithms import parse_dfa
from gambatools.nfa import NFA
from gambatools.nfa_algorithms import parse_nfa, nfa_to_dfa, epsilon_closure
from gambatools.notebook import show, show_nfa2dfa, print_feedback


def check_nfa_to_dfa_answer(N: NFA, answer: NFA):
    def state(q: Set[State]) -> State:
        return State(print_state_set(q))

    def extract_states(q: State) -> Set[State]:
        label: str = q
        if re.fullmatch(r'{.*}', label):
            label = label[1:-1]
        if label:
            return set(State(s) for s in label.split(','))
        else:
            return set([])

    D = nfa_to_dfa(N)

    feedback = []

    if len(answer.Q) == 0:
        feedback.append('Error: the set of states is empty')

    if N.Sigma != answer.Sigma:
        feedback.append('Error: the alphabet is wrong')

    # check if the states in answer.Q have the right format
    for q in answer.Q:
        if not re.fullmatch(state_set_regex(), q):
            feedback.append("Error: the state label {} has the wrong format".format(q))
            break
        if not extract_states(q) <= N.Q:
            q1 = next(iter(extract_states(q) - N.Q))
            feedback.append("Error: the element {} in {} is not a state of the original NFA".format(q1, q))

    # check the initial state
    if extract_states(answer.q0) != extract_states(D.q0):
        feedback.append('Error: the initial state is incorrect')

    # check the final states
    for q in answer.Q:
        q_states = extract_states(q)
        is_final = not q_states.isdisjoint(N.F)
        if (q in answer.F) != is_final:
            feedback.append('Error: the state {} should {}be marked as final'.format(q, '' if is_final else 'not '))
            break

    # check the transition targets
    for q, a in itertools.product(answer.Q, answer.Sigma):
        q_states = extract_states(q)
        Q1 = answer.delta[q, a]
        if len(Q1) != 1:
            continue
        q1 = next(iter(Q1))
        q1_states = extract_states(q1)

        q1_states_expected = set([])
        for q_ in q_states:
            q1_states_expected |= N.delta[q_, a]
        q1_states_expected = epsilon_closure(N, q1_states_expected)

        if q1_states != q1_states_expected:
            feedback.append('Error: the {}-transition from {} has the wrong target {}'.format(a, print_state_set(q_states), state(q1_states)))
            break

    # check if the states are deterministic and total
    for q, a in itertools.product(answer.Q, answer.Sigma):
            Q1 = answer.delta[q, a]
            if len(Q1) == 0:
                feedback.append('Error: the state {} has no outgoing {}-transition'.format(q, a))
                break
            if len(Q1) > 1:
                feedback.append('Error: the state {} has multiple outgoing {}-transitions'.format(q, a))
                break

    return feedback


def check_nfa2dfa(nfa: str, dfa: str) -> None:
    try:
        N = parse_nfa(nfa)
        answer: NFA = parse_nfa(dfa, state_regex=state_set_regex())  # N.B. We use an NFA, to avoid the strict DFA checking
        feedback = check_nfa_to_dfa_answer(N, answer)
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))
