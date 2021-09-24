#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Set, MutableMapping, Tuple, Mapping

from gambatools.dfa import State, Symbol, print_alphabet, print_state_set


class PDA(object):
    def __init__(self,
                 Q: Set[State],
                 Sigma: Set[Symbol],
                 Gamma: Set[Symbol],
                 delta: MutableMapping[Tuple[State, Symbol, Symbol], Set[Tuple[State, Symbol]]],
                 q0: State,
                 F: Set[State],
                 epsilon: Symbol = Symbol(''),
                 check_validity: bool = True):
        self.Q = Q
        self.Sigma = Sigma
        self.Gamma = Gamma
        self.delta = delta
        self.q0 = q0
        self.F = F
        self.epsilon = epsilon

        if check_validity:
            self._check_validity()

    def _check_validity(self):
        Q = self.Q
        Sigma = self.Sigma
        Gamma = self.Gamma
        delta = self.delta
        q0 = self.q0
        F = self.F
        epsilon = self.epsilon
        assert q0 in Q
        assert epsilon not in Sigma
        assert epsilon not in Gamma
        assert F <= Q
        for (p, a, u), Q1 in delta.items():
            assert p in Q
            assert a in Sigma | {epsilon}
            assert u in Gamma | {epsilon}
            for (q, v) in Q1:
                assert q in Q
                assert v in Gamma | {epsilon}

    def is_push_pop_transition(self, p: State, a: Symbol, u: Symbol, q: State, v: Symbol) -> bool:
        epsilon = self.epsilon
        return (u == epsilon and v != epsilon) or (u != epsilon and v == epsilon)

    def __str__(self):
        return print_pda(self)


def print_pda_delta(delta: Mapping[Tuple[State, Symbol, Symbol], Set[Tuple[State, Symbol]]]):
    if len(delta) == 0:
        return 'delta = {:}'
    result = []
    for (p, a, u), Q1 in delta.items():
        result.append('delta({}, {}, {}) = {}'.format(p, a, u, Q1))
    return '\n'.join(sorted(result))


def print_pda(P: PDA) -> str:
    return 'Q = {}\nSigma = {}\nGamma = {}\n{}\nq0 = {}\nF = {}'.format(print_state_set(P.Q), print_alphabet(P.Sigma), print_alphabet(P.Gamma), print_pda_delta(P.delta), P.q0, print_state_set(P.F))
