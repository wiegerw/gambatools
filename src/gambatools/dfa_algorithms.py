#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import copy
import itertools
import io
from collections import defaultdict
from typing import Set, MutableMapping, Tuple, Mapping, List

from gambatools.automaton import Automaton
from gambatools.automaton_algorithms import default_transition_label_regex, default_state_label_regex, AutomatonParser, AutomatonBuilder
from gambatools.dfa import State, Symbol, print_state_set, DFA
from gambatools.nfa import NFA


def dfa_accepts_word(D: DFA, word: str) -> bool:
    delta = D.delta
    q0 = D.q0
    F = D.F

    q = q0
    for a in word:
        q = delta[q, a]
    return q in F


def dfa_simulate_word(D: DFA, word: str) -> List[Tuple[State, str]]:
    delta = D.delta
    q0 = D.q0

    q = q0
    k = 0
    result = [(q0, word)]
    for a in word:
        k = k + 1
        q = delta[q, a]
        result.append((q, word[:-k]))
    return result


def dfa_words_up_to_n(D: DFA, n: int) -> Set[str]:
    words = set([])
    if D.q0 in D.F:
        words.add('')
    W = {(D.q0, '')}
    for i in range(n):
        W1 = set([])
        for (q, word) in W:
            for a in D.Sigma:
                q1 = D.delta[q, a]
                word1 = word + a
                W1.add((q1, word1))
                if q1 in D.F:
                    words.add(word1)
        W = W1
    return words


def dfa_make_total_in_place(D: DFA) -> None:
    Q = D.Q
    Sigma = D.Sigma
    delta = D.delta
    q_trap = fresh_state(Q, 'trap')
    Q.add(q_trap)
    for q in Q:
        for a in Sigma:
            if not (q, a) in delta:
                delta[q, a] = q_trap


def dfa_make_total(D: DFA) -> DFA:
    D = copy.deepcopy(D)
    dfa_make_total(D)
    return D


def dfa_minimize(D: DFA) -> DFA:
    def print_element(table, i, j):
        if j < i:
            return ' '
        return '1' if table[i, j] else '0'

    def print_table(table: MutableMapping[Tuple[int, int], bool], N: int):
        lines = []
        for i in range(N):
            lines.append(''.join([print_element(table, i, j) for j in range(N)]))
        print('\n'.join(lines))

    Q = D.Q
    Sigma = D.Sigma
    delta = D.delta
    F = D.F
    q = list(Q)
    n = len(q)

    table: MutableMapping[Tuple[int, int], bool] = {}
    for i, j in itertools.combinations_with_replacement(range(n), 2):
        table[i, j] = ((q[i] in F) == (q[j] in F))

    # print_table(table, n)

    changed = True
    while changed:
        changed = False
        for i, j in itertools.combinations(range(n), 2):
            if table[i, j]:
                for a in Sigma:
                    k = q.index(delta[q[i], a])
                    l = q.index(delta[q[j], a])
                    if not table[min(k, l), max(k, l)]:
                        table[i, j] = False
                        changed = True
                        break

    # print_table(table, n)

    return dfa_from_table(D, table)


def dfa_from_table(D: DFA, table: Mapping[Tuple[int, int], bool]) -> DFA:
    def state(q: Set[State]) -> State:
        return State(print_state_set(q))

    Q = D.Q
    Sigma = D.Sigma
    delta = D.delta
    q0 = D.q0
    F = D.F
    q = list(Q)
    n = len(q)

    Q_: List[Set[State]] = [set([]) for _ in range(n)]
    R: Set[State] = set([])
    for i in range(n):
        if q[i] not in R:
            Q_[i].add(q[i])
            R.add(q[i])
            for j in range(i + 1, n):
                if table[i, j]:
                    Q_[i].add(q[j])
                    R.add(q[j])

    Q_r: Set[State] = set(map(state, Q_))
    F_r: Set[State] = set(state(Q_[i]) for i in range(n) if q[i] in F)
    q_r = state(next(Q_i for Q_i in Q_ if q0 in Q_i))
    delta_r: MutableMapping[Tuple[State, Symbol], State] = {}
    for i in range(n):
        Q_i = state(Q_[i])
        for a in Sigma:
            q1 = delta[q[i], a]
            Q_j = state(next(x for x in Q_ if q1 in x))
            delta_r[Q_i, a] = Q_j

    return DFA(Q_r, Sigma, delta_r, q_r, F_r)


def dfa_isomorphic(D1: DFA, D2: DFA) -> bool:
    assert D1.Sigma == D2.Sigma
    Sigma = D1.Sigma
    Q1 = D1.Q
    Q2 = D2.Q
    F1 = D1.F
    F2 = D2.F

    matching = {(q1, q2): False for (q1, q2) in itertools.product(Q1, Q2)}

    if (D1.q0 in F1) == (D2.q0 in F2):
        matching[D1.q0, D2.q0] = True
        to_inspect = {(D1.q0, D2.q0)}
    else:
        return False

    while len(to_inspect) > 0:
        (q1, q2) = next(iter(to_inspect))
        to_inspect.remove((q1, q2))
        for a in Sigma:
            q1_ = D1.delta[q1, a]
            q2_ = D2.delta[q2, a]
            if matching[q1_, q2_]:
                if (q1_ in F1) == (q2_ in F2):
                    matching[q1_, q2_] = True
                    to_inspect.add((q1_, q2_))
                else:
                    return False

    for q1 in Q1:
        count = 1
        for q2 in Q2:
            if matching[q1, q2]:
                count = count + 1
        if count != 1:
            return False

    for q2 in Q2:
        count = 1
        for q1 in Q1:
            if matching[q1, q2]:
                count = count + 1
        if count != 1:
            return False

    return True


def dfa_isomorphic1(D1: DFA, D2: DFA) -> bool:
    assert D1.Sigma == D2.Sigma
    Sigma = D1.Sigma
    F1 = D1.F
    F2 = D2.F

    matching = {}
    todo = {(D1.q0, D2.q0)}

    while len(todo) > 0:
        (q1, q2) = next(iter(todo))
        todo.remove((q1, q2))
        if (q1 in F1) != (q2 in F2):
            return False
        matching[q1] = q2
        for a in Sigma:
            q1_ = D1.delta[q1, a]
            q2_ = D2.delta[q2, a]
            if q1_ not in matching:
                todo.add((q1_, q2_))
            elif q2_ != matching[q1_]:
                return False

    return True


def random_dfa(Sigma: Set[Symbol], n: int) -> DFA:
    import random

    Q: Set[State] = set([State('q{}'.format(i)) for i in range(n)])
    delta: MutableMapping[Tuple[State, Symbol], State] = {}
    q0: State = next(q for q in Q if q == State('q0'))
    F: Set[State] = set([])

    # generate delta
    for q in Q:
        for a in Sigma:
            q1 = random.choice(list(Q))
            delta[q, a] = q1

    # generate F
    for q in Q:
        if random.randint(0, 5) <= 2:
            F.add(q)

    return DFA(Q, Sigma, delta, q0, F)


def print_dfa(D: DFA) -> str:
    Q = D.Q
    Sigma = D.Sigma
    delta = D.delta
    q0 = D.q0
    F = D.F

    out = io.StringIO()
    out.write('states {}\n'.format(' '.join(sorted(Q))))
    out.write('final {}\n'.format(' '.join(sorted(F))))
    out.write('initial {}\n'.format(q0))
    out.write('input_symbols {}\n'.format(' '.join(sorted(Sigma))))
    transitions = defaultdict(lambda: [])
    for (p, a), q in delta.items():
        transitions['{} {}'.format(p, q)].append(a)
    for pq in sorted(transitions.keys()):
        out.write('{} {}\n'.format(pq, ' '.join(transitions[pq])))
    result = out.getvalue()
    out.close()
    return result.strip()


def fresh_state(Q: Set[State], hint: str = 'P') -> State:
    index = 1
    while True:
        q = State('{}{}'.format(hint, index))
        if q not in Q:
            return q
        index = index + 1


def automaton_to_dfa(A: Automaton, transition_regex=default_transition_label_regex(), state_regex=default_state_label_regex()) -> DFA:
    return DFABuilder(A, state_regex=state_regex, transition_regex=transition_regex).build()


def parse_dfa(text: str, transition_regex=default_transition_label_regex(), state_regex=default_state_label_regex()) -> DFA:
    A = AutomatonParser(state_regex=state_regex, transition_regex=transition_regex).parse(text)
    return automaton_to_dfa(A, state_regex=state_regex, transition_regex=transition_regex)


class DFABuilder(AutomatonBuilder):
    def __init__(self, A: Automaton, state_regex=r'\w+', transition_regex=r'\w+'):
        super().__init__(A, state_regex, transition_regex)

    def used_input_symbols(self) -> Set[str]:
        A = self.A
        return set(a for (_, a, _) in A.transitions)

    def _check_is_deterministic(self):
        A = self.A
        V = set()
        for (p, a, _) in A.transitions:
            if (p, a) in V:
                raise RuntimeError('the automaton is not deterministic in node {}'.format(p))
            V.add((p, a))

    def _check_is_total(self, input_symbols: Set[str]):
        A = self.A
        V = set((p, a) for (p, a, _) in A.transitions)
        for p in A.states:
            for a in input_symbols:
                if (p, a) not in V:
                    raise RuntimeError('the automaton is not total in node {}'.format(p))

    def build(self) -> DFA:
        A = self.A
        A.states = A.states if len(A.states) > 0 else A.used_states()

        self._check_states_are_declared()
        self._check_state_labels()
        self._check_one_initial_state()
        self._check_is_deterministic()
        input_symbols = self.get_symbol_set('input_symbols', self.used_input_symbols())
        self._check_symbols(input_symbols)
        self._check_is_total(input_symbols)

        Q = set(State(s) for s in A.states)
        Sigma = set(Symbol(s) for s in input_symbols)
        delta = {}
        q0 = State(next(iter(A.initial_states)))
        F = set(State(s) for s in A.final_states)
        for (p, a, q) in A.transitions:
            p = State(p)
            q = State(q)
            a = Symbol(a)
            delta[p, a] = q
        return DFA(Q, Sigma, delta, q0, F)


# def dfa_product(D1: DFA, D2: DFA) -> DFA:
#     Q1 = D1.Q
#     Sigma1 = D1.Sigma
#     delta1 = D1.delta
#     q01 = D1.q0
#     F1 = D1.F
#
#     Q2 = D2.Q
#     Sigma2 = D2.Sigma
#     delta2 = D2.delta
#     q02 = D2.q0
#     F2 = D2.F
#
#     def make_state(q1: State, q2: State) -> State:
#         return State('({},{})'.format(q1,q2))
#
#     def make_symbol(a1: Symbol, a2: Symbol) -> Symbol:
#         return Symbol('{}{}'.format(a1,a2))
#
#     states = list(itertools.product(Q1, Q2))
#     symbols = list(itertools.product(Sigma1, Sigma2))
#     final_states = itertools.product(F1, F2)
#
#     Q = set(make_state(q1,q2) for q1,q2 in states)
#     Sigma = set(make_symbol(a1, a2) for a1,a2 in symbols)
#     delta = { (make_state(q1, q2), make_symbol(a1, a2)) : make_state(delta1[q1, a1], delta2[q2, a2]) for (q1, q2), (a1, a2) in itertools.product(states, symbols) }
#     q0 = make_state(q01,q02)
#     F = set(make_state(q1,q2) for q1,q2 in final_states)
#
#     return DFA(Q, Sigma, delta, q0, F)


def dfa_complement(D: DFA) -> DFA:
    Q = D.Q
    Sigma = D.Sigma
    delta = D.delta
    q0 = D.q0
    F = D.F
    return DFA(Q, Sigma, delta, q0, Q - F)


def dfa_product(D1: DFA, D2: DFA, product_type: str) -> DFA:
    Q1 = D1.Q
    Sigma1 = D1.Sigma
    delta1 = D1.delta
    q01 = D1.q0
    F1 = D1.F

    Q2 = D2.Q
    Sigma2 = D2.Sigma
    delta2 = D2.delta
    q02 = D2.q0
    F2 = D2.F

    assert Sigma1 == Sigma2

    def make_state(q1: State, q2: State) -> State:
        return State('({},{})'.format(q1,q2))

    states = list(itertools.product(Q1, Q2))
    if product_type == 'union':
        final_states = list((q1, q2) for (q1, q2) in states if q1 in F1 or q2 in F2)
    elif product_type == 'intersection':
        final_states = list((q1, q2) for (q1, q2) in states if q1 in F1 and q2 in F2)
    elif product_type == 'symmetric_difference':
        final_states = list((q1, q2) for (q1, q2) in states if (q1 in F1 and q2 not in F2) or (q1 not in F1 and q2 in F2))
    else:
        raise RuntimeError('unknown product type {}'.format(product_type))

    Q = set(make_state(q1,q2) for q1,q2 in states)
    Sigma = Sigma1
    delta = { (make_state(q1, q2), a) : make_state(delta1[q1, a], delta2[q2, a]) for (q1, q2), a in itertools.product(states, Sigma) }
    q0 = make_state(q01,q02)
    F = set(make_state(q1,q2) for q1,q2 in final_states)

    return DFA(Q, Sigma, delta, q0, F)


# union of two regular languages: product automaton with synchronized
# transitions (p,q) -a-> (p',q') if p -a-> p' and q -a-> q' and final
# states { (p,q) | p in F_1 or q in F_2
def dfa_union(D1: DFA, D2: DFA) -> DFA:
    return dfa_product(D1, D2, 'union')


# intersection of two regular languages: product automaton with synchronized
# transitions (p,q) -a-> (p',q') if p -a-> p' and q -a-> q' and final
# states { (p,q) | p in F_1 and q in F_2
def dfa_intersection(D1: DFA, D2: DFA) -> DFA:
    return dfa_product(D1, D2, 'intersection')


# symmetric difference of two regular languages: product automaton with synchronized
# transitions (p,q) -a-> (p',q') if p -a-> p' and q -a-> q' and final
# states { (p,q) | (p in F_1 and q not in F_2) or (p not in F_1 and q in F_2)
def dfa_symmetric_difference(D1: DFA, D2: DFA) -> DFA:
    return dfa_product(D1, D2, 'symmetric_difference')


def dfa_reverse(D: DFA) -> NFA:
    epsilon = Symbol('ε')

    q0 = fresh_state(D.Q, 'q')
    Q = D.Q.copy() | {q0}
    Sigma = D.Sigma.copy()
    delta = defaultdict(set)
    for (q, a), q1 in D.delta.items():
        delta[q1, a].add(q)
    delta[q0, epsilon] = D.F.copy()
    F = {D.q0}

    return NFA(Q, Sigma, delta, q0, F, epsilon)


def dfa_no_prefix(D: DFA) -> NFA:
    epsilon = Symbol('ε')

    Q = D.Q.copy()
    Sigma = D.Sigma.copy()
    delta = defaultdict(set)
    for (q, a), q1 in D.delta.items():
        if q not in D.F:
            delta[q, a].add(q1)
    q0 = D.q0
    F = D.F.copy()

    return NFA(Q, Sigma, delta, q0, F, epsilon)


# Returns the states reachable from q with a path of length >= depth
def dfa_reachable_states(D: DFA, q: State, depth=0) -> Set[State]:
    discovered = {q} if depth == 0 else set()

    d = 0
    V = {q}  # V contains reachable nodes at depth d

    while True:
        Vnext = set()
        for u, a in itertools.product(V, D.Sigma):
            v = D.delta[u, a]
            if v not in discovered:
                discovered.add(v)
                Vnext.add(v)
        if not Vnext:
            break
        d = d + 1
        V = Vnext

    return discovered


def dfa_no_extend(D: DFA) -> DFA:
    Q = D.Q.copy()
    Sigma = D.Sigma.copy()
    delta = dict(D.delta)
    q0 = D.q0
    F = set(qf for qf in D.F if len(dfa_reachable_states(D, qf, 1) & D.F) == 0)

    return DFA(Q, Sigma, delta, q0, F)
