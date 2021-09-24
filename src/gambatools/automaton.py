#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Set, List, Tuple, Mapping, Any


class Automaton(object):
    def __init__(self,
                 states: Set[str],
                 transitions: List[Tuple[str, str, str]],
                 initial_states: Set[str],
                 final_states: Set[str],
                 items: Mapping[str, List[Any]]
                ):
        self.states = states
        self.transitions = transitions
        self.initial_states = initial_states
        self.final_states = final_states
        self.items = items

    def used_states(self) -> Set[str]:
        result = self.initial_states | self.final_states
        for (p, _, q) in self.transitions:
            result.add(p)
            result.add(q)
        return result
