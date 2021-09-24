#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List, Set, Iterable, Optional, Tuple
from collections import defaultdict
import copy
import itertools
import io

from gambatools.automaton import Automaton
from gambatools.automaton_algorithms import default_state_label_regex, AutomatonParser, AutomatonBuilder, pda_keywords

from gambatools.dfa import State, Symbol
from gambatools.dfa_algorithms import fresh_state
from gambatools.pda import PDA
from gambatools.cfg import CFG, Variable, Terminal, Rule, Alternative


def pda_is_push_pop(P: PDA) -> bool:
    """Returns true if the following property holds:
       Each transition either pushes a symbol onto the stack (a push move) or pops
       one off the stack (a pop move), but it does not do both at the same time.
    :param P:
    :return:
    """
    delta = P.delta
    return all([P.is_push_pop_transition(p, a, u, q, v)  for (p, a, u), Q1 in delta.items() for (q, v) in Q1])


# TODO: implement a more robust solution
def fresh_symbol(Sigma: Set[str], symbols: Iterable[str]) -> Symbol:
    for s in symbols:
        symbol = Symbol(s)
        if symbol not in Sigma:
            return symbol
    raise RuntimeError('Could not find a fresh symbol in {}'.format(symbols))


def pda_to_one_accepting_state_in_place(P: PDA) -> None:
    """Modifies P such that it has exactly one accepting state"""

    Q = P.Q
    delta = P.delta
    F = P.F
    epsilon = P.epsilon

    if len(F) == 1:
        return

    q_accept = fresh_state(Q, 'q_accept')
    Q.add(q_accept)

    for q in F:
        delta[q, epsilon, epsilon].add((q_accept, epsilon))

    F.clear()
    F.add(q_accept)


def pda_to_accept_on_empty_stack_in_place(P: PDA) -> None:
    """Modifies P such that it only accepts on empty stack"""

    Q = P.Q
    q0 = P.q0
    delta = P.delta
    Gamma = P.Gamma
    F = P.F
    epsilon = P.epsilon

    stack_bottom = fresh_symbol(Gamma, '$@#*&!?')
    Gamma.add(stack_bottom)

    # define a new initial state
    q_initial = fresh_state(Q, 'q_initial')
    Q.add(q_initial)
    delta[q_initial, epsilon, epsilon].add((q0, stack_bottom))
    P.q0 = q_initial

    # define a new accepting state
    q_accept = fresh_state(Q, 'q_accept')
    Q.add(q_accept)
    for q in F:
        delta[q, epsilon, stack_bottom].add((q_accept, epsilon))
    F.clear()
    F.add(q_accept)


def pda_to_accept_on_empty_stack(P: PDA) -> PDA:
    P = copy.deepcopy(P)
    pda_to_accept_on_empty_stack_in_place(P)
    return P


def pda_to_push_pop_in_place(P: PDA) -> None:
    """Brings the PDA P in push/pop format"""

    Q = P.Q
    Gamma = P.Gamma
    delta = P.delta
    F = P.F
    epsilon = P.epsilon

    pda_to_one_accepting_state_in_place(P)

    # add intermediate states to enforce push/pop transitions
    dummy = Symbol('∅')
    assert dummy not in Gamma # TODO: implement a robust solution
    Gamma.add(dummy)
    delta1 = defaultdict(lambda: set([]))
    for (p, a, u), Q1 in delta.items():
        for (q, v) in Q1:
            if P.is_push_pop_transition(p, a, u, q, v):
                delta1[p, a, u].add((q, v))
            elif u == epsilon and v == epsilon:
                q_mid = fresh_state(Q, 'M')
                Q.add(q_mid)
                delta1[p, a, epsilon].add((q_mid, dummy))
                delta1[q_mid, epsilon, dummy].add((q, epsilon))
            elif u != epsilon and v != epsilon:
                q_mid = fresh_state(Q, 'M')
                Q.add(q_mid)
                delta1[p, a, u].add((q_mid, epsilon))
                delta1[q_mid, epsilon, epsilon].add((q, v))
    delta.clear()
    delta.update(delta1)


def pda_to_push_pop(P: PDA) -> PDA:
    """Brings the PDA P in push/pop format"""
    P = copy.deepcopy(P)
    pda_to_push_pop_in_place(P)
    return P


def pda_to_cfg(P: PDA, accepts_on_empty_stack: bool = False) -> CFG:
    """Implements the algorithm in Sipser 3rd ed. page 122.
    """

    P = copy.deepcopy(P)

    if len(P.F) != 1:
        pda_to_one_accepting_state_in_place(P)

    if not pda_is_push_pop(P):
        pda_to_push_pop_in_place(P)

    if not accepts_on_empty_stack:
        pda_to_accept_on_empty_stack_in_place(P)

    def variable(p: State, q: State) -> Variable:
        return Variable("{}'{}".format(p, q))

    Q = P.Q
    Sigma = P.Sigma
    Gamma = P.Gamma
    delta = P.delta
    q0 = P.q0
    F = P.F
    epsilon = Terminal(P.epsilon)
    q_accept = next(iter(F))

    def make_rule(A, a):
        return Rule(A, Alternative([value for value in a if value != epsilon]))

    V: Set[Variable] = {variable(p, q) for (p, q) in itertools.product(Q, repeat=2)}
    Sigma1: Set[Terminal] = set([Terminal(a) for a in Sigma])
    R: List[Rule] = []
    S: Variable = variable(q0, q_accept)

    T_pop = defaultdict(lambda: [])
    T_push = defaultdict(lambda: [])
    for (p, a, u), Q1 in delta.items():
        for (q, v) in Q1:
            if u == epsilon:
                T_push[v].append((p, a, u, q, v))
            else:
                T_pop[u].append((p, a, u, q, v))

    for u in Gamma:
        for (p, a, _, r, _), (s, b, _, q, _) in itertools.product(T_push[u], T_pop[u]):
            Apq = variable(p, q)
            Ars = variable(r, s)
            a_ = Terminal(a)
            b_ = Terminal(b)
            R.append(make_rule(Apq, [a_, Ars, b_]))

    for (p, q, r) in itertools.product(Q, repeat=3):
        Apq = variable(p, q)
        Apr = variable(p, r)
        Arq = variable(r, q)
        R.append(make_rule(Apq, [Apr, Arq]))

    for p in Q:
        App = variable(p, p)
        R.append(make_rule(App, []))

    return CFG(V, Sigma1, R, S, epsilon)


class PDAState(object):
    def __init__(self, q: State, stack: List[Symbol]):
        self.q = q
        self.stack = stack[:]

    def __str__(self):
        return '({}, [{}])'.format(self.q, ''.join(self.stack))

    def __eq__(self, other):
        return self.q == other.q and self.stack == other.stack

    def __hash__(self):
        return hash(str(self)) # TODO: improve the efficiency

    def __lt__(self, other):
        return str(self) < str(other)  # TODO: improve the efficiency


def pda_can_pop_push(P: PDA, stack: List[Symbol], u: Symbol, v: Symbol) -> bool:
    """Returns true if u can be popped from and then v pushed on stack"""
    return u == P.epsilon or (stack and stack[-1] == u)


def pda_pop_push(P: PDA, stack: List[Symbol], u: Symbol, v: Symbol) -> List[Symbol]:
    """Tries to pop u from and push v on stack. Returns a copy of the resulting stack"""
    epsilon = P.epsilon
    if u == epsilon:
        if v == epsilon:
            return stack[:]
        else:
            return stack + [v]
    else:
        if not stack or stack[-1] != u:
            raise RuntimeError('pda_pop_push({}, {}, {}) is not possible!'.format(stack, u, v))
        if v == epsilon:
            return stack[:-1]
        else:
            return stack[:-1] + [v]


def pda_epsilon_closure(P: PDA, R: Iterable[PDAState]) -> Set[PDAState]:
    """Returns all states reachable from an element in R via epsilon steps."""
    delta = P.delta
    epsilon = P.epsilon

    result: Set[PDAState] = set([r for r in R])
    todo: Set[PDAState] = set([r for r in R])
    while len(todo) > 0:
        src = todo.pop()
        for (p, a, u), Q1 in delta.items():
            if p != src.q or a != epsilon:
                continue
            for (q, v) in Q1:
                if pda_can_pop_push(P, src.stack, u, v):
                    stack1 = pda_pop_push(P, src.stack, u, v)
                    target = PDAState(q, stack1)
                    if target not in result:
                        todo.add(target)
                        result.add(target)
    return result


def pda_do_transition(P: PDA, a: Symbol, R: Iterable[PDAState]) -> Set[PDAState]:
    """Returns all PDA states reachable from an element in R via an a-transition."""
    delta = P.delta

    result: Set[PDAState] = set([])
    for r in R:
        p, stack = r.q, r.stack
        for (p1, a1, u), Q1 in delta.items():
            if p != p1 or a != a1:
                continue
            for (q, v) in Q1:
                if pda_can_pop_push(P, stack, u, v):
                    stack1 = pda_pop_push(P, stack, u, v)
                    r1 = PDAState(q, stack1)
                    # print('transition {}{} {},{}->{}'.format(p1, q, a1, u, v))
                    # print('p = {}'.format(p))
                    # print('r1 = {}'.format(r1))
                    result.add(r1)
    return result


def pda_find_epsilon_path(P: PDA, R: Set[PDAState], f: PDAState) -> Optional[List[PDAState]]:
    """Returns a path from an element r in R to f"""
    delta = P.delta
    epsilon = P.epsilon

    if f in R:
        return [f]

    backpointers = {}

    def make_path(q: PDAState) -> List[PDAState]:
        path = [q]
        while q not in R:
            q = backpointers[q]
            path.insert(0, q)
        return path

    visited: Set[PDAState] = set([r for r in R])
    todo: Set[PDAState] = set([r for r in R])
    while len(todo) > 0:
        src = todo.pop()
        for (p, a, u), Q1 in delta.items():
            if p != src.q or a != epsilon:
                continue
            for (q, v) in Q1:
                if pda_can_pop_push(P, src.stack, u, v):
                    stack1 = pda_pop_push(P, src.stack, u, v)
                    target = PDAState(q, stack1)
                    backpointers[target] = src
                    if target == f:
                        return make_path(target)
                    if target not in visited:
                        todo.add(target)
                        visited.add(target)
    return None


def pda_find_transition(P: PDA, R: Set[PDAState], a: Symbol, target: PDAState) -> Optional[PDAState]:
    """Returns src such that src --a--> target"""
    delta = P.delta
    for src in R:
        for (p, a1, u), Q1 in delta.items():
            if src.q != p or a != a1:
                continue
            for (q, v) in Q1:
                if q == target.q and pda_can_pop_push(P, src.stack, u, v) and pda_pop_push(P, src.stack, u, v) == target.stack:
                    return src
    return None


def pda_accepts_word(P: PDA, w: str) -> bool:
    F = P.F
    R = {PDAState(P.q0, [])}
    R = pda_epsilon_closure(P, R)
    for a in w:
        R = pda_do_transition(P, Symbol(a), R)
        R = pda_epsilon_closure(P, R)
    return any(r.q in F for r in R)


def pda_simulate_word(P: PDA, w: str) -> Optional[Tuple[State, str, List[Symbol]]]:
    F = P.F
    H = []

    def make_row(r: PDAState, word: str):
        return (r.q, word, r.stack[:])

    R = {PDAState(P.q0, [])}
    H.append(R)
    R = pda_epsilon_closure(P, R)
    H.append(R)

    for a in w:
        R = pda_do_transition(P, Symbol(a), R)
        H.append(R)
        R = pda_epsilon_closure(P, R)
        H.append(R)

    if any(r.q in F for r in R):
        S = H.pop()
        front = next(r for r in S if r.q in F)
        result = [make_row(front, '')]
        word = ''
        for a in reversed(w):
            S = H.pop()
            path = pda_find_epsilon_path(P, S, front)
            result = [make_row(r, word) for r in path[:-1]] + result
            front = path[0]
            S = H.pop()
            front = pda_find_transition(P, S, a, front)
            word = a + word
            result = [make_row(front, word)] + result
        S = H.pop()
        path = pda_find_epsilon_path(P, S, front)
        result = [make_row(r, word) for r in path[:-1]] + result
        return result
    else:
        return None


def pda_words_up_to_n(P: PDA, n: int) -> Set[str]:
    F = P.F
    Sigma = P.Sigma

    result = set([])
    W = defaultdict(lambda: set([]))
    R = {PDAState(P.q0, [])}
    R = pda_epsilon_closure(P, R)
    for r in R:
        W[r] = {''}
        if r.q in F:
            result.add('')

    for i in range(n):
        W1 = defaultdict(lambda: set([]))
        for r, words in W.items():
            for a in Sigma:
                R = pda_do_transition(P, a, {r})
                R = pda_epsilon_closure(P, R)
                words_plus_a = set(word + a for word in words)
                for r1 in R:
                    W1[r1] |= words_plus_a
                    if r1.q in F:
                        result |= words_plus_a
        W = W1
    return result


def print_pda(P: PDA) -> str:
    Q = P.Q
    Sigma = P.Sigma
    Gamma = P.Gamma
    delta = P.delta
    q0 = P.q0
    F = P.F
    epsilon = P.epsilon

    out = io.StringIO()
    out.write('states {}\n'.format(' '.join(sorted(Q))))
    out.write('final {}\n'.format(' '.join(sorted(F))))
    out.write('initial {}\n'.format(q0))
    out.write('input_symbols {}\n'.format(' '.join(sorted(Sigma))))
    out.write('stack_symbols {}\n'.format(' '.join(sorted(Gamma))))
    out.write('epsilon {}\n'.format(epsilon))
    transitions = defaultdict(lambda: [])
    for (p, a, u), Q1 in delta.items():
        for (q, v) in Q1:
            transitions['{} {}'.format(p, q)].append('{},{}{}'.format(a, u, v))
    for pq in sorted(transitions.keys()):
        out.write('{} {}\n'.format(pq, ' '.join(transitions[pq])))
    result = out.getvalue()
    out.close()
    return result


def pda_transition_transition_regex() -> str:
    s = r'[\w\d~!@#$%^&*]'
    return r'\w,{0}{0}'.format(s)


def automaton_to_pda(A: Automaton, transition_regex = pda_transition_transition_regex(), state_regex = default_state_label_regex()) -> PDA:
    return PDABuilder(A, state_regex=state_regex, transition_regex=transition_regex).build()


def parse_pda(text: str, transition_regex = pda_transition_transition_regex(), state_regex = default_state_label_regex()) -> PDA:
    A = AutomatonParser(state_regex=state_regex, transition_regex=transition_regex, keywords = pda_keywords()).parse(text)
    return automaton_to_pda(A, state_regex=state_regex, transition_regex=transition_regex)


class PDABuilder(AutomatonBuilder):
    def __init__(self, A: Automaton, state_regex=r'\w+', transition_regex=r'\w+'):
        super().__init__(A, state_regex, transition_regex)

    def used_input_symbols(self, epsilon: str) -> Set[str]:
        A = self.A
        return set(label[0] for (_, label, _) in A.transitions if label[0] != epsilon)

    def used_stack_symbols(self, epsilon: str) -> Set[str]:
        A = self.A
        result = set([])
        for (_, label, _) in A.transitions:
            result.add(label[2])
            result.add(label[3])
        return result - {epsilon}

    def build(self) -> PDA:
        A = self.A
        A.states = A.states if len(A.states) > 0 else A.used_states()

        self._check_states_are_declared()
        self._check_state_labels()
        self._check_one_initial_state()
        epsilon = self.parse_symbol()
        input_symbols = self.get_symbol_set('input_symbols', self.used_input_symbols(epsilon))
        stack_symbols = self.get_symbol_set('stack_symbols', self.used_stack_symbols(epsilon))
        self._check_symbols(input_symbols)

        Q = set(State(s) for s in A.states)
        Sigma = set(Symbol(s) for s in input_symbols)
        Gamma = set(Symbol(s) for s in stack_symbols)
        delta = defaultdict(set)
        q0 = State(next(iter(A.initial_states)))
        F = set(State(s) for s in A.final_states)
        epsilon = Symbol(epsilon)

        for (p, label, q) in A.transitions:
            p = State(p)
            q = State(q)
            a, _, u, v = label
            a = Symbol(a)
            u = Symbol(u)
            v = Symbol(v)
            delta[p, a, u].add((q, v))
        return PDA(Q, Sigma, Gamma, delta, q0, F, epsilon)
