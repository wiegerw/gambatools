#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import NewType, Set, Mapping, Tuple

from gambatools.dfa import State, Symbol, print_alphabet, print_state_set

Direction = NewType('Direction', str)


class TM(object):
    def __init__(self,
                 Q: Set[State],
                 Sigma: Set[Symbol],
                 Gamma: Set[Symbol],
                 delta: Mapping[Tuple[State, Symbol], Tuple[State, Symbol, Direction]],
                 q0: State,
                 q_accept: State,
                 q_reject: State,
                 blank: Symbol = Symbol('_'),
                 check_validity: bool = True):
        self.Q = Q
        self.Sigma = Sigma
        self.Gamma = Gamma
        self.delta = delta
        self.q0 = q0
        self.q_accept = q_accept
        self.q_reject = q_reject
        self.blank = blank

        if check_validity:
            self._check_validity()

    def _check_validity(self):
        Q = self.Q
        Sigma = self.Sigma
        Gamma = self.Gamma
        delta = self.delta
        q0 = self.q0
        q_accept = self.q_accept
        q_reject = self.q_reject
        blank = self.blank
        assert q0 in Q
        assert q_accept in Q
        assert q_reject in Q
        assert q_reject != q_accept
        assert blank not in Sigma
        assert blank in Gamma
        assert Sigma <= Gamma
        for (p, a), (q, b, d) in delta.items():
            assert p in Q
            assert a in Gamma
            assert q in Q
            assert b in Gamma
            assert d in ['L', 'R']
        # total, witness = self.is_total()
        # if not total:
        #     q, a = witness
        #     print('The TM is not total: transition ({},{}) is missing'.format(q, a))

    def is_total(self):
        Q = self.Q
        Gamma = self.Gamma
        delta = self.delta
        blank = self.blank
        q_accept = self.q_accept
        q_reject = self.q_reject
        for q in Q - {q_accept, q_reject}:
            for a in Gamma - {blank}:
                if (q, a) not in delta:
                    return False, (q, a)
        return True, None

    def __str__(self):
        return print_tm(self)


def print_tm_delta(delta: Mapping[Tuple[State, Symbol], Tuple[State, Symbol, Direction]]):
    if len(delta) == 0:
        return 'delta = {:}'
    result = []
    for (p, a), (q, b, d) in delta.items():
        result.append('delta({}, {}) = ({}, {}, {})'.format(p, a, q, b, d))
    return '\n'.join(sorted(result))


def print_tm(T: TM) -> str:
    return 'Q = {}\nSigma = {}\nGamma = {}\n{}\nq0 = {}\nq_accept = {}\nq_reject = {}'.format(print_state_set(T.Q), print_alphabet(T.Sigma), print_alphabet(T.Gamma), print_tm_delta(T.delta), T.q0, T.q_accept, T.q_reject)
