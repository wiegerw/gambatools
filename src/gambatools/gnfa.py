#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Mapping, Set, Tuple

from gambatools.dfa import State, Symbol, print_alphabet, print_state_set
from gambatools.regexp import Regexp


def print_gnfa_delta(delta: Mapping[Tuple[State, State], Regexp]):
    if len(delta) == 0:
        return 'delta = {:}'
    result = []
    for (q1, q2), r in delta.items():
        result.append('delta({}, {}) = {}'.format(q1, q2, r))
    return '\n'.join(sorted(result))


class GNFA(object):
    def __init__(self, Q: Set[State], Sigma: Set[Symbol], delta: Mapping[Tuple[State, State], Regexp], q_start: State, q_accept: State, epsilon: Symbol = Symbol('')):
        self.Q  = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q_start = q_start
        self.q_accept = q_accept
        self.epsilon = epsilon

        self.check_validity()

    def check_validity(self):
        Q = self.Q
        Sigma = self.Sigma
        delta = self.delta
        q_start = self.q_start
        q_accept = self.q_accept
        epsilon = self.epsilon
        # TODO: check if q_start and q_accept should be in Q or not
        # assert q_start not in Q
        # assert q_accept not in Q
        assert epsilon not in Sigma
        for (q1, q2) in delta:
            assert q1 in Q
            assert q2 in Q

    def __str__(self):
        return print_gnfa(self)


def print_gnfa(G: GNFA) -> str:
    return 'Q = {}\nSigma = {}\n{}\nq_start = {}\nq_accept = {}'.format(print_state_set(G.Q), print_alphabet(G.Sigma), print_gnfa_delta(G.delta), G.q_start, G.q_accept)
