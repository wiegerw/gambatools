#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Set, Mapping, Tuple, Union

from gambatools.dfa import State, Symbol, print_alphabet, print_state_set, print_delta


class NFA(object):
    def __init__(self, Q: Set[State], Sigma: Set[Symbol], delta: Mapping[Tuple[State, Symbol], Set[State]], q0: State, F: Set[State], epsilon: Symbol = Symbol(''), check_validity: bool = True):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q0 = q0
        self.F = F
        self.epsilon = epsilon

        if check_validity:
            self._check_validity()

    def _check_validity(self):
        Q = self.Q
        Sigma = self.Sigma
        delta = self.delta
        q0 = self.q0
        F = self.F
        epsilon = self.epsilon
        assert q0 in Q
        assert F <= Q
        assert epsilon not in Sigma
        for (q, a) in delta:
            Q1 = delta[q, a]
            assert q in Q
            assert a in Sigma | {epsilon}
            assert Q1 <= Q

    def E(self, q: Union[State, Set[State]]):
        from gambatools.nfa_algorithms import epsilon_closure
        return epsilon_closure(self, q)

    def __str__(self):
        return _print_nfa(self)


def _print_nfa(N: NFA) -> str:
    return 'Q = {}\nSigma = {}\n{}\nq0 = {}\nF = {}\nepsilon = {}'.format(print_state_set(N.Q), print_alphabet(N.Sigma), print_delta(N.delta), N.q0, print_state_set(N.F), N.epsilon)
