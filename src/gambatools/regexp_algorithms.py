#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from collections import defaultdict
import itertools
from typing import Set, MutableMapping, Tuple

from gambatools.gnfa import GNFA

from gambatools.regexp import *
from gambatools.dfa import State, Symbol as nfaSymbol, DFA
from gambatools.nfa import NFA
from gambatools.identifier_generator import IdentifierGenerator
from gambatools.regexp import Regexp


def regexp_size(r: Regexp) -> int:
    if isinstance(r, (Zero, One, Symbol)):
        return 0
    elif isinstance(r, Iteration):
        return regexp_size(r.operand) + 1
    elif isinstance(r, (Concat, Sum)):
        return regexp_size(r.left) + regexp_size(r.right) + 2


def regexp_symbols(r: Regexp) -> Set[Symbol]:
    if isinstance(r, (Zero, One)):
        return set([])
    elif isinstance(r, Symbol):
        return {r}
    elif isinstance(r, Iteration):
        return regexp_symbols(r.operand)
    elif isinstance(r, (Sum, Concat)):
        return regexp_symbols(r.left) | regexp_symbols(r.right)


class RegexpToNFAGenerator(object):
    def __init__(self):
        self.Sigma: Set[nfaSymbol] = set([])
        self.id_generator = IdentifierGenerator()  # TODO: take care of name clashes

    def fresh_state(self):
        q = State(self.id_generator.generate('q'))
        return q

    def generate_zero(self) -> NFA:
        q0 = self.fresh_state()
        Q = {q0}
        F = set([])
        delta = defaultdict(lambda: set([]))
        return NFA(Q, self.Sigma, delta, q0, F)

    def generate_one(self) -> NFA:
        q0 = self.fresh_state()
        Q = {q0}
        F = {q0}
        delta = defaultdict(lambda: set([]))
        return NFA(Q, self.Sigma, delta, q0, F)

    def generate_symbol(self, x: Symbol) -> NFA:
        a: nfaSymbol = nfaSymbol(x.symbol)
        self.Sigma.add(a)
        q0 = self.fresh_state()
        q1 = self.fresh_state()
        Q = {q0, q1}
        F = {q1}
        delta = defaultdict(lambda: set([]))
        delta[q0, a] = {q1}
        return NFA(Q, self.Sigma, delta, q0, F)

    def generate(self, x: Regexp) -> NFA:
        from gambatools.nfa_algorithms import nfa_repetition, nfa_union, nfa_concatenation
        if isinstance(x, Zero):
            return self.generate_zero()
        elif isinstance(x, One):
            return self.generate_one()
        elif isinstance(x, Symbol):
            return self.generate_symbol(x)
        elif isinstance(x, Iteration):
            return nfa_repetition(self.generate(x.operand), self.id_generator)
        elif isinstance(x, Sum):
            return nfa_union(self.generate(x.left), self.generate(x.right), self.id_generator)
        elif isinstance(x, Concat):
            return nfa_concatenation(self.generate(x.left), self.generate(x.right))
        raise RuntimeError('RegexpToNFAGenerator.generate: unexpected case {}'.format(x))


def regexp_to_nfa(x: Regexp) -> NFA:
    return RegexpToNFAGenerator().generate(x)


def regexp_simplify(r: Regexp) -> Regexp:
    if isinstance(r, (Zero, One, Symbol)):
        result = r
    elif isinstance(r, Iteration):
        operand = regexp_simplify(r.operand)
        if isinstance(operand, (Zero, One)):
            result = One()
        elif isinstance(operand, Iteration):
            result = operand
        else:
            result = Iteration(operand)
    elif isinstance(r, Sum):
        left = regexp_simplify(r.left)
        right = regexp_simplify(r.right)
        if isinstance(left, Zero):
            result = right
        elif isinstance(right, Zero):
            result = left
        else:
            result = Sum(left, right)
    elif isinstance(r, Concat):
        left = regexp_simplify(r.left)
        right = regexp_simplify(r.right)
        if isinstance(left, Zero):
            result = Zero()
        elif isinstance(left, One):
            result = right
        elif isinstance(right, Zero):
            result = Zero()
        elif isinstance(right, One):
            result = left
        else:
            result = Concat(left, right)
    else:
        raise RuntimeError('Could not simplify ', r)
    # print('regexp_simplify({}) = {}'.format(x, result))
    return result


def regexp_accepts_word(r: Regexp, w: str) -> bool:
    """A naive implementation of regexp matching"""
    result = None
    if isinstance(r, Zero):
        result = False
    elif isinstance(r, One):
        result = (len(w) == 0)
    elif isinstance(r, Symbol):
        result = (w == r.symbol)
    elif isinstance(r, Sum):
        result = regexp_accepts_word(r.left, w) or regexp_accepts_word(r.right, w)
    elif isinstance(r, Concat):
        result = any(regexp_accepts_word(r.left, w[:k]) and regexp_accepts_word(r.right, w[k:]) for k in range(len(w) + 1))
    elif isinstance(r, Iteration):
        if len(w) == 0:
            result = True
        else:
            result = any(regexp_accepts_word(r.operand, w[:k]) and regexp_accepts_word(r, w[k:]) for k in range(1, len(w) + 1))
    # print('regexp_accepts_word({}, {}) = {}'.format(x, w, result))
    return result


def concatenate(L1: Set[str], L2: Set[str]) -> Set[str]:
    result = set([x + y for (x, y) in itertools.product(L1, L2)])
    # print('concatenate({}, {}) = {}'.format(L1, L2, result))
    return result


def regexp_words_up_to_n(r: Regexp, n: int) -> Set[str]:
    """A naive implementation of language generation"""
    result = None
    if isinstance(r, Zero):
        result = set([])
    elif isinstance(r, One):
        result = {''}
    elif isinstance(r, Symbol):
        result = {r.symbol} if n > 0 else set([])
    elif isinstance(r, Sum):
        result = regexp_words_up_to_n(r.left, n) | regexp_words_up_to_n(r.right, n)
    elif isinstance(r, Concat):
        result = set().union(*[concatenate(regexp_words_up_to_n(r.left, k), regexp_words_up_to_n(r.right, n - k)) for k in range(n + 1)])
    elif isinstance(r, Iteration):
        if n == 0:
            result = {''}
        else:
            result = {''} | set().union(*[concatenate(regexp_words_up_to_n(r.operand, k), regexp_words_up_to_n(r, n - k)) for k in range(1, n + 1)])
    # print('regexp_words_up_to_n({}, {}) = {}'.format(x, n, print_words(result)))
    return result


def random_regexp(Sigma: Set[nfaSymbol], size: int) -> Regexp:
    import random
    if size == 0:
        percentage = random.randint(1, 100)
        if percentage <= 15:
            result = Zero()
        elif percentage <= 30:
            result = One()
        else:
            result = Symbol(random.choice(list(Sigma)))
    elif size == 1:
        result = Iteration(random_regexp(Sigma, size - 1))
    else:
        percentage = random.randint(1, 100)
        if percentage <= 33:
            result = Iteration(random_regexp(Sigma, size - 1))
        elif percentage <= 66:
            k = random.randint(0, size - 2)
            result = Concat(random_regexp(Sigma, k), random_regexp(Sigma, size - k - 2))
        else:
            k = random.randint(0, size - 2)
            result = Sum(random_regexp(Sigma, k), random_regexp(Sigma, size - k - 2))
    # print('random_regexp({}, {}) = {}  size = {}'.format(print_words(Sigma), size, result, regexp_size(result)))
    return result


def dfa_to_gnfa(D: DFA) -> GNFA:
    from gambatools import regexp
    Q = D.Q
    Sigma = D.Sigma
    delta = D.delta
    q0 = D.q0
    F = D.F

    # TODO: use an identifier generator to avoid name clashes
    q_start = State('start')
    q_accept = State('accept')
    assert q_start not in Q
    assert q_accept not in Q

    Q1: Set[State] = Q | {q_accept, q_start}
    delta1 = defaultdict(lambda: regexp.Zero())  # MutableMapping[Tuple[State, State], regexp.Regexp]

    delta1[q_start, q0] = regexp.One()

    for q in F:
        delta1[q, q_accept] = regexp.One()

    for (q, a), q1 in delta.items():
        if (q, q1) in delta1:
            delta1[q, q1] = regexp.Sum(delta1[q, q1], regexp.Symbol(a))
        else:
            delta1[q, q1] = regexp.Symbol(a)

    return GNFA(Q1, Sigma, delta1, q_start, q_accept)


def dfa_to_regexp(D: DFA) -> Regexp:
    G: GNFA = dfa_to_gnfa(D)
    gnfa_minimize(G)
    return G.delta[G.q_start, G.q_accept]


def gnfa_minimize(G: GNFA) -> None:
    from gambatools.regexp import Regexp, Concat, Sum, Iteration

    Q: Set[State] = G.Q
    delta: MutableMapping[Tuple[State, State], Regexp] = G.delta
    q_start: State = G.q_start
    q_accept: State = G.q_accept

    for q_rip in Q - {q_start, q_accept}:
        Q.remove(q_rip)
        R2 = delta[q_rip, q_rip]
        for q_i in Q - {q_accept}:
            R1 = delta[q_i, q_rip]
            for q_j in Q - {q_start}:
                R3 = delta[q_rip, q_j]
                R4 = delta[q_i, q_j]
                R = regexp_simplify(Sum(Concat(R1, Concat(Iteration(R2), R3)), R4))
                delta[q_i, q_j] = R
    r = delta[q_start, q_accept]
    delta.clear()
    delta[q_start, q_accept] = r
