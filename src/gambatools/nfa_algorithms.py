#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from collections import defaultdict
from typing import Set, Mapping, MutableMapping, Tuple, Union, List, Optional
import io

from gambatools.automaton import Automaton
from gambatools.automaton_algorithms import default_transition_label_regex, default_state_label_regex, AutomatonParser, AutomatonBuilder, \
    nfa_keywords
from gambatools.dfa import State, Symbol, print_state_set, DFA
from gambatools.nfa import NFA
from gambatools.identifier_generator import IdentifierGenerator


def _nfa_cache(N: NFA) -> Tuple[Mapping[State, Set[State]], Mapping[Tuple[State, Symbol], Set[State]]]:
    # make a cache of epsilon_closure(q)
    Eq: MutableMapping[State, Set[State]] = {}
    for q in N.Q:
        Eq[q] = epsilon_closure(N, q)

    # make a cache of epsilon_closure(delta(q,a))
    Eqa = defaultdict(set)  # Eqa: TypedDict[State, Set[str]]
    for (q, a), Q in N.delta.items():
        Eqa[(q, a)] = set().union(*[Eq[q] for q in Q]) if Q else set([])

    return Eq, Eqa


def epsilon_closure(N: NFA, q: Union[State, Set[State]]) -> Set[State]:
    result: Set[State] = q.copy() if isinstance(q, set) else {q}
    todo: Set[State] = result.copy()
    while todo:
        q = todo.pop()
        Q1: Set[State] = N.delta[q, N.epsilon] - result
        result = result | Q1
        todo = todo | Q1
    return result


def nfa_accepts_word(N: NFA, word: str) -> bool:
    q0 = N.q0
    F = N.F
    Eq, Eqa = _nfa_cache(N)
    q: Set[State] = Eq[q0]
    for a in word:
        q = set().union(*[Eqa[q_i, Symbol(a)] for q_i in q])
    return not q.isdisjoint(F)


def nfa_words_up_to_n(N: NFA, n: int) -> Set[str]:
    Eq, Eqa = _nfa_cache(N)

    # F contains all states that can terminate
    F1 = [q for q in N.Q if not Eq[q].isdisjoint(N.F)]

    result = set([])
    if N.q0 in F1:
        result.add('')

    W = defaultdict(lambda: set([]))  # W: TypedDict[State, Set[str]]
    for q in Eq[N.q0]:
        W[q] = {''}

    for i in range(n):
        W1 = defaultdict(lambda: set([]))  # W1: TypedDict[State, Set[str]]
        for (q, words) in W.items():
            for a in N.Sigma:
                if (q, a) in Eqa:
                    for q1 in Eqa[(q, a)]:
                        words_q1 = set([word + a for word in words])
                        W1[q1] |= words_q1
                        if q1 in F1:
                            result |= words_q1
        W = W1
    return result


def nfa_do_transition(N: NFA, a: Symbol, R: Set[State]) -> Set[State]:
    """Returns all NFA states reachable from an element in R via an a-transition."""
    delta = N.delta
    result: Set[State] = set([])
    for r in R:
        if (r, a) in delta:
            result |= delta[r, a]
    return result

def nfa_find_epsilon_path(N: NFA, R: Set[State], f: State) -> Optional[List[State]]:
    """Returns a path from an element r in R to f"""
    delta = N.delta
    epsilon = N.epsilon

    if f in R:
        return [f]

    backpointers = {}

    def make_path(q: State) -> List[State]:
        path = [q]
        while q not in R:
            q = backpointers[q]
            path.insert(0, q)
        return path

    visited: Set[State] = set([r for r in R])
    todo: Set[State] = set([r for r in R])
    while len(todo) > 0:
        src = todo.pop()
        for (p, a), Q1 in delta.items():
            if p != src or a != epsilon:
                continue
            for q in Q1:
                target = q
                backpointers[target] = src
                if target == f:
                    return make_path(target)
                if target not in visited:
                    todo.add(target)
                    visited.add(target)
    return None


def nfa_find_transition(N: NFA, R: Set[State], a: Symbol, target: State) -> Optional[State]:
    """Returns src such that src --a--> target"""
    delta = N.delta
    for src in R:
        for (p, a1), Q1 in delta.items():
            if src != p or a != a1:
                continue
            for q in Q1:
                if q == target:
                    return src
    return None


def nfa_simulate_word(N: NFA, w: str) -> Optional[Tuple[State, str]]:
    F = N.F
    H = []

    R = {N.q0}
    H.append(R)
    R = epsilon_closure(N, R)
    H.append(R)

    for a in w:
        R = nfa_do_transition(N, Symbol(a), R)
        H.append(R)
        R = epsilon_closure(N, R)
        H.append(R)

    if any(r in F for r in R):
        S = H.pop()
        front = next(r for r in S if r in F)
        result = [(front, '')]
        word = ''
        for a in reversed(w):
            S = H.pop()
            path = nfa_find_epsilon_path(N, S, front)
            result = [(r, word) for r in path[:-1]] + result
            front = path[0]
            S = H.pop()
            front = nfa_find_transition(N, S, a, front)
            word = a + word
            result = [(front, word)] + result
        S = H.pop()
        path = nfa_find_epsilon_path(N, S, front)
        result = [(r, word) for r in path[:-1]] + result
        return result
    else:
        return None


def nfa_to_dfa(N: NFA) -> DFA:
    def state(q: Set[State]) -> State:
        return State(print_state_set(q))

    Sigma: Set[Symbol] = N.Sigma.copy()
    F: Set[State] = set([])
    Q0: Set[State] = epsilon_closure(N, {N.q0})
    stateQ0 = state(Q0)
    Q: Set[State] = {stateQ0}
    delta: MutableMapping[Tuple[State, Symbol], State] = {}
    if not Q0.isdisjoint(N.F):
        F.add(stateQ0)
    todo = [Q0]

    while todo:
        Q1 = todo.pop()
        stateQ1 = state(Q1)

        for a in Sigma:
            Q2 = set([])
            for q1 in Q1:
                Q2 |= N.delta[q1, a]
            Q2 = epsilon_closure(N, Q2)
            stateQ2 = state(Q2)
            delta[stateQ1, a] = stateQ2
            if not Q2.isdisjoint(N.F):
                F.add(stateQ2)
            if stateQ2 not in Q:
                Q.add(stateQ2)
                todo.append(Q2)

    return DFA(Q, Sigma, delta, stateQ0, F)


def random_nfa(Sigma: Set[Symbol], n: int) -> NFA:
    import random

    Q: Set[State] = set([State('q{}'.format(i)) for i in range(n)])
    delta: MutableMapping[Tuple[State, Symbol], Set[State]] = {}
    q0: State = next(q for q in Q if q == State('q0'))
    F: Set[State] = set([])
    epsilon = Symbol('')

    # generate delta
    for q in Q:
        for a in Sigma | {epsilon}:
            k = random.choice(range(min(n + 1, 3)))
            Q1 = set(random.sample(list(Q), k))
            delta[q, a] = Q1

    # generate F
    for q in Q:
        if random.randint(0, 5) <= 2:
            F.add(q)
    return NFA(Q, Sigma, delta, q0, F, epsilon)


def nfa_repetition(N: NFA, id_generator: IdentifierGenerator = IdentifierGenerator()) -> NFA:
    Sigma = N.Sigma
    q0 = State(id_generator.generate('q'))
    Q = N.Q | {q0}
    F = N.F | {q0}
    delta = defaultdict(lambda: set([]))
    delta.update(N.delta)
    for q in F:
        delta[q, N.epsilon] |= {N.q0}
    delta[q0, N.epsilon] = {N.q0}
    return NFA(Q, Sigma, delta, q0, F)


def nfa_union(N1: NFA, N2: NFA, id_generator: IdentifierGenerator = IdentifierGenerator()) -> NFA:
    assert N1.Q.isdisjoint(N2.Q)
    Sigma = N1.Sigma | N2.Sigma
    q0 = State(id_generator.generate('q'))
    Q = N1.Q | N2.Q | {q0}
    F = N1.F | N2.F
    delta = defaultdict(lambda: set([]))
    delta.update(N1.delta)
    delta.update(N2.delta)
    delta[q0, N1.epsilon] = {N1.q0, N2.q0}
    return NFA(Q, Sigma, delta, q0, F)


def nfa_concatenation(N1: NFA, N2: NFA) -> NFA:
    assert N1.Q.isdisjoint(N2.Q)
    Sigma = N1.Sigma | N2.Sigma
    q0 = N1.q0
    Q = N1.Q | N2.Q | {q0}
    F = N2.F
    delta = defaultdict(lambda: set([]))
    delta.update(N1.delta)
    delta.update(N2.delta)
    for q in N1.F:
        delta[q, N1.epsilon] |= {N2.q0}
    return NFA(Q, Sigma, delta, q0, F)


def print_nfa(N: NFA) -> str:
    Q = N.Q
    Sigma = N.Sigma
    delta = N.delta
    q0 = N.q0
    F = N.F
    epsilon = N.epsilon

    out = io.StringIO()
    out.write('states {}\n'.format(' '.join(sorted(Q))))
    out.write('final {}\n'.format(' '.join(sorted(F))))
    out.write('initial {}\n'.format(q0))
    out.write('input_symbols {}\n'.format(' '.join(sorted(Sigma))))
    out.write('epsilon {}\n'.format(epsilon))
    transitions = defaultdict(lambda: [])
    for (p, a), Q1 in delta.items():
        for q in Q1:
            transitions['{} {}'.format(p, q)].append(a)
    for pq in sorted(transitions.keys()):
        out.write('{} {}\n'.format(pq, ' '.join(transitions[pq])))
    result = out.getvalue()
    out.close()
    return result


def automaton_to_nfa(A: Automaton, transition_regex = default_transition_label_regex(), state_regex = default_state_label_regex()) -> NFA:
    return NFABuilder(A, state_regex=state_regex, transition_regex=transition_regex).build()


def parse_nfa(text: str, transition_regex = default_transition_label_regex(), state_regex = default_state_label_regex()) -> NFA:
    A = AutomatonParser(state_regex=state_regex, transition_regex=transition_regex, keywords = nfa_keywords()).parse(text)
    return automaton_to_nfa(A, state_regex=state_regex, transition_regex=transition_regex)


class NFABuilder(AutomatonBuilder):
    def __init__(self, A: Automaton, state_regex=r'\w+', transition_regex=r'\w+'):
        super().__init__(A, state_regex, transition_regex)

    def used_input_symbols(self, epsilon: str) -> Set[str]:
        A = self.A
        return set(a for (_, a, _) in A.transitions if a != epsilon)

    def build(self) -> NFA:
        A = self.A
        A.states = A.states if len(A.states) > 0 else A.used_states()

        self._check_states_are_declared()
        self._check_state_labels()
        self._check_one_initial_state()
        epsilon = self.parse_symbol()
        input_symbols = self.get_symbol_set('input_symbols', self.used_input_symbols(epsilon))
        self._check_symbols(input_symbols)

        Q = set(State(s) for s in A.states)
        Sigma = set(Symbol(s) for s in input_symbols)
        delta = defaultdict(set)
        q0 = State(next(iter(A.initial_states)))
        F = set(State(s) for s in A.final_states)
        epsilon = Symbol(epsilon)
        for (p, a, q) in A.transitions:
            p = State(p)
            q = State(q)
            a = Symbol(a)
            delta[p, a].add(q)
        return NFA(Q, Sigma, delta, q0, F, epsilon)
