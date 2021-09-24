#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import re
from collections import defaultdict
from typing import Any, Callable, Set

import graphviz


def make_label_default(label: str) -> str:
    if len(label) == 4 and label[1] == ',':  # assume it is a PDA transition
        label = re.sub('_', 'ε', label)
        a, _, u, v = label
        return '{},{}→{}'.format(a, u, v)
    elif len(label) == 4 and label[2] == ',':  # assume it is a TM transition
        label = re.sub('_', '□', label)
        a, b, _, d = label
        return '{}→{},{}'.format(a, b, d)
    else:
        return re.sub('_', 'ε', label)


def automaton_to_dot(A: Any, join_labels: bool = True, make_label: Callable[[str], str] = make_label_default) -> graphviz.Digraph:
    Q = A.states
    I = A.initial_states
    F = A.final_states

    d = graphviz.Digraph()
    d.attr(rankdir='LR')

    for q in Q:
        if q in F:
            d.node(q, peripheries='2', fontname='Times-Italic', fontsize='11')
        else:
            d.node(q, fontname='Times-Italic', fontsize='11')
        if q in I:
            q_fake = fresh_identifier(Q, 'fake')
            d.node(q_fake, style='invisible')
            d.edge(q_fake, q, fontname='Times-Italic', fontsize='11')

    if join_labels:
        edge_map = defaultdict(list)
        for (p, a, q) in A.transitions:
            edge_map[p, q].append(make_label(a))
        transitions = [(p, a, q) for (p, q), a in edge_map.items()]
    else:
        transitions = [(p, [a], q) for (p, a, q) in A.transitions]

    for (p, a, q) in transitions:
        label = ','.join(a)
        if len(label) > 7:
            label = '\n'.join(a)
        d.edge(p, q, label=label, fontname='Times-Italic', fontsize='11')
    return d


def fresh_identifier(Q: Set[str], hint: str = 'P') -> str:
    if hint not in Q:
        return hint
    index = 1
    while True:
        q = '{}{}'.format(hint, index)
        if q not in Q:
            return q
        index = index + 1
