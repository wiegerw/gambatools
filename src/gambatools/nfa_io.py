#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from gambatools.dfa import State, Symbol
from gambatools.nfa import NFA


def nfa_to_dot(N: NFA) -> str:
    from gambatools.dfa_io import DOT_AUTOMATON_TEXT

    def state(q: State) -> str:
        attributes = []
        if q == N.q0:
            attributes.append('root = true')
        if q in N.F:
            attributes.append('shape = doublecircle')
        return '  "{}" [{}]'.format(q, ', '.join(attributes)) if attributes else '  "{}"'.format(q)

    def transition(q: State, a: Symbol, q1: State) -> str:
        if not a:
            a = 'ε'
        return '  "{}" -> "{}" [label="{}"]'.format(q, q1, a)

    text = DOT_AUTOMATON_TEXT
    text = text.replace('<INITIALSTATE>', N.q0)
    text = text.replace('<STATES>', '\n'.join([state(q) for q in N.Q]))
    text = text.replace('<TRANSITIONS>', '\n'.join([transition(q, a, q1) for (q, a), Q1 in N.delta.items() for q1 in Q1]))
    return text
