#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import NewType, Set, Mapping, Tuple

State = NewType('State', str)
Symbol = NewType('Symbol', str)


def print_alphabet(Sigma: Set[Symbol]) -> str:
    if len(Sigma) == 0:
        return '{}'
    return State('{{ {} }}'.format(', '.join(sorted(Sigma))))


def print_state_set(Q: Set[State]) -> str:
    if len(Q) == 0:
        return '{}'
    return '{{{}}}'.format(','.join(sorted(Q)))


def print_delta(delta):
    if len(delta) == 0:
        return 'delta = {:}'
    result = []
    for (q, a) in delta:
        q1 = delta[q, a]
        q1 = q1 if isinstance(q1, str) else sorted(q1)
        if a == '':
            a = 'epsilon'
        result.append('delta({}, {}) = {}'.format(q, a, q1))
    return '\n'.join(sorted(result))


class DFA(object):
    def __init__(self, Q: Set[State], Sigma: Set[Symbol], delta: Mapping[Tuple[State, Symbol], State], q0: State, F: Set[State], check_validity: bool = True):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q0 = q0
        self.F = F

        if check_validity:
            self._check_validity()

    def _check_validity(self):
        Q = self.Q
        Sigma = self.Sigma
        delta = self.delta
        q0 = self.q0
        F = self.F
        assert q0 in Q
        assert F <= Q
        for (q, a) in delta:
            q1 = delta[q, a]
            assert q in Q
            assert a in Sigma
            assert q1 in Q
        assert self._is_total()

    def _is_total(self):
        Q = self.Q
        Sigma = self.Sigma
        delta = self.delta
        for q in Q:
            for a in Sigma:
                if (q, a) not in delta:
                    return False
        return True

    def __str__(self):
        return 'Q = {}\nSigma = {}\n{}\nq0 = {}\nF = {}'.format(print_state_set(self.Q), print_alphabet(self.Sigma), print_delta(self.delta), self.q0, print_state_set(self.F))
