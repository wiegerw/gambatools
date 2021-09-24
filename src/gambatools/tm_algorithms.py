#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List, Set, Tuple, Optional
from collections import defaultdict
import itertools
import io

from gambatools.automaton import Automaton
from gambatools.automaton_algorithms import default_state_label_regex, AutomatonParser, AutomatonBuilder, tm_keywords

from gambatools.dfa import State, Symbol
from gambatools.tm import Direction, TM


def print_tm_state(q, tape, head):
    print(''.join(tape), q)
    print(' ' * head + '^')


def tm_do_transition(T: TM, p: State, tape: List[Symbol], head: int) -> Tuple[State, int]:
    """Does a transition of a Turing Machine, and returns the new state and tape position. The tape is modified."""
    if p in [T.q_reject, T.q_accept]:
        raise RuntimeError('tm_do_transition: can not do a transition in the accepting or rejecting state')

    a = tape[head]
    if (p, a) in T.delta:
        q, b, d = T.delta[p, a]
    else:
        q, b, d = T.q_reject, a, Direction('R')
    tape[head] = b
    head1 = max(head - 1, 0) if d == 'L' else head + 1

    if head1 == len(tape):
        tape.append(T.blank)

    return q, head1


def tm_accepts_word(T: TM, word: str, max_steps: int = 1000) -> Optional[bool]:
    q0 = T.q0
    q_accept = T.q_accept
    q_reject = T.q_reject
    q = q0

    tape = [Symbol(w_i) for w_i in word]
    head = 0
    if head == len(tape):
        tape.append(T.blank)

    for _ in range(max_steps):
        q, head = tm_do_transition(T, q, tape, head)
        if q == q_accept:
            return True
        if q == q_reject:
            return False
    return None


def tm_simulate_word(T: TM, word: str, max_steps: int = 1000) -> List[Tuple[State, List[str], int]]:
    q0 = T.q0
    q_accept = T.q_accept
    q_reject = T.q_reject
    q = q0

    result = []

    tape = [Symbol(w_i) for w_i in word]
    head = 0
    if head == len(tape):
        tape.append(T.blank)
    result.append((q, tape[:], head))

    for _ in range(max_steps):
        q, head = tm_do_transition(T, q, tape, head)
        result.append((q, tape[:], head))
        if q == q_accept:
            break
        if q == q_reject:
            break
    return result


def tm_words_up_to_n(T: TM, n: int, max_steps: int = 1000) -> Set[str]:
    Sigma = T.Sigma
    result = set([])
    for i in range(n + 1):
        for w in itertools.product(Sigma, repeat = i):
            word = ''.join(w)
            if tm_accepts_word(T, word, max_steps):
                result.add(word)
    return result


def print_tm(P: TM) -> str:
    Q = P.Q
    Sigma = P.Sigma
    Gamma = P.Gamma
    delta = P.delta
    q0 = P.q0
    q_accept = P.q_accept
    q_reject = P.q_reject
    blank = P.blank

    out = io.StringIO()
    out.write('states {}\n'.format(' '.join(sorted(Q))))
    out.write('initial {}\n'.format(q0))
    out.write('accept {}\n'.format(q_accept))
    out.write('reject {}\n'.format(q_reject))
    out.write('input_symbols {}\n'.format(' '.join(sorted(Sigma))))
    out.write('tape_symbols {}\n'.format(' '.join(sorted(Gamma))))
    out.write('blank {}\n'.format(blank))
    transitions = defaultdict(lambda: [])
    for (p, a), (q, b, d) in delta.items():
        transitions['{} {}'.format(p, q)].append('{}{},{}'.format(a, b, d))
    for pq in sorted(transitions.keys()):
        out.write('{} {}\n'.format(pq, ' '.join(transitions[pq])))
    result = out.getvalue()
    out.close()
    return result


def tm_transition_transition_regex() -> str:
    s = r'[\w\d~!@#$%^&*□]'
    return r'{0}{0},[LR]'.format(s)


def automaton_to_tm(A: Automaton, transition_regex = tm_transition_transition_regex(), state_regex = default_state_label_regex()) -> TM:
    return TMBuilder(A, state_regex=state_regex, transition_regex=transition_regex).build()


def parse_tm(text: str, transition_regex = tm_transition_transition_regex(), state_regex = default_state_label_regex()) -> TM:
    A = AutomatonParser(state_regex=state_regex, transition_regex=transition_regex, keywords = tm_keywords()).parse(text)
    return automaton_to_tm(A, state_regex=state_regex, transition_regex=transition_regex)


class TMBuilder(AutomatonBuilder):
    def __init__(self, A: Automaton, state_regex=r'\w+', transition_regex=r'\w+'):
        super().__init__(A, state_regex, transition_regex)

    def used_tape_symbols(self) -> Set[str]:
        A = self.A
        result = set([])
        for (_, label, _) in A.transitions:
            result.add(label[0])
            result.add(label[1])
        return result

    def build(self) -> TM:
        A = self.A
        q_accept = self.get_state('accept', self._fresh_state(A.states, 'accept'))
        q_reject = self.get_state('reject', self._fresh_state(A.states, 'reject'))
        A.states = A.states if len(A.states) > 0 else A.used_states() | {q_accept, q_reject}

        self._check_states_are_declared()
        self._check_state_labels()
        self._check_one_initial_state()
        blank = self.parse_symbol('blank', '□', '_')
        tape_symbols = self.get_symbol_set('tape_symbols', self.used_tape_symbols())
        input_symbols = self.get_symbol_set('input_symbols')
        if not input_symbols:
            input_symbols = tape_symbols - {blank}

        Q = set(State(s) for s in A.states)
        Sigma = set(Symbol(s) for s in input_symbols)
        Gamma = set(Symbol(s) for s in tape_symbols)
        delta = defaultdict(set)
        q0 = State(next(iter(A.initial_states)))
        blank = Symbol(blank)
        q_accept = State(q_accept)
        q_reject = State(q_reject)

        for (p, label, q) in A.transitions:
            p = State(p)
            q = State(q)
            a, b, _, d = label
            a = Symbol(a)
            b = Symbol(b)
            d = Direction(d)
            delta[p, a] = (q, b, d)
        return TM(Q, Sigma, Gamma, delta, q0, q_accept, q_reject, blank)
