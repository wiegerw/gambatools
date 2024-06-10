#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Set, Mapping, Tuple, List, Any
import graphviz
from gambatools.automaton import Automaton

from gambatools.dfa import DFA, State, Symbol
from gambatools.automaton_io import automaton_to_dot

DOT_AUTOMATON_TEXT = '''digraph
{
  fake [style=invisible]
  fake -> "<INITIALSTATE>" [style=bold]

<STATES>

<TRANSITIONS>
}
'''


def dfa_to_dot(D: DFA) -> str:
    def state(q: State) -> str:
        attributes = []
        if q == D.q0:
            attributes.append('root = true')
        if q in D.F:
            attributes.append('shape = doublecircle')
        return '  "{}" [{}]'.format(q, ', '.join(attributes)) if attributes else '  "{}"'.format(q)

    def transition(q: State, a: Symbol, q1: State) -> str:
        return '  "{}" -> "{}" [label="{}"]'.format(q, q1, a)

    text = DOT_AUTOMATON_TEXT
    text = text.replace('<INITIALSTATE>', D.q0)
    text = text.replace('<STATES>', '\n'.join([state(q) for q in D.Q]))
    text = text.replace('<TRANSITIONS>', '\n'.join([transition(q, a, q1) for (q, a), q1 in D.delta.items()]))
    return text


def draw_dfa(Q: Set[State], Sigma: Set[Symbol], delta: Mapping[Tuple[State, Symbol], State], q0: State, F: Set[State]) -> graphviz.Digraph:
    states = Q
    transitions = [(p, a, q) for (p, a), q in delta.items()]
    initial_states = {q0}
    final_states = F
    items = {}
    A = Automaton(states, transitions, initial_states, final_states, items)
    return automaton_to_dot(A)