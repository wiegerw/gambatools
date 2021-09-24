#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List, FrozenSet, Set, Optional
import re

from gambatools.automaton import Automaton


def default_state_label_regex() -> str:
    return r'\w+'


def default_transition_label_regex() -> str:
    return r'.+'


def default_symbol_regex() -> str:
    return r'\w+'


def state_set_regex() -> str:
    return r'\{[\w,]*\}'


def state_product_regex() -> str:
    return r'\(\w+,\w+\)'


def dfa_keywords() -> FrozenSet[str]:
    return frozenset(['input_symbols'])


def nfa_keywords() -> FrozenSet[str]:
    return frozenset(['input_symbols', 'epsilon'])


def pda_keywords() -> FrozenSet[str]:
    return frozenset(['input_symbols', 'stack_symbols', 'epsilon'])


def tm_keywords() -> FrozenSet[str]:
    return frozenset(['input_symbols', 'tape_symbols', 'blank', 'accept', 'reject'])


def automaton_keywords() -> FrozenSet[str]:
    return dfa_keywords() | nfa_keywords() | pda_keywords() | tm_keywords()


class AutomatonBuilder(object):
    def __init__(self, A: Automaton, state_regex = default_state_label_regex(), transition_regex=default_transition_label_regex(), symbol_regex=default_symbol_regex()):
        self.A = A
        self.state_regex = state_regex
        self.transition_regex = transition_regex
        self.symbol_regex = symbol_regex

    def _fresh_state(self, states: Set[str], hint: str = 'P') -> str:
        if hint not in states:
            return hint
        index = 1
        while True:
            state = '{}{}'.format(hint, index)
            if state not in states:
                return state
            index = index + 1

    def _check_symbol(self, symbol):
        if not re.fullmatch(self.symbol_regex, symbol):
            raise RuntimeError('invalid symbol {}'.format(symbol))

    def _check_symbols(self, symbols):
        for symbol in symbols:
            self._check_symbol(symbol)

    def _check_state_label(self, state) -> None:
        if not re.fullmatch(self.state_regex, state):
            raise RuntimeError('invalid state label {}'.format(state))

    def _check_transition_label(self, label) -> None:
        if not re.fullmatch(self.transition_regex, label):
            raise RuntimeError('invalid transition label {}'.format(label))

    def _check_state_labels(self):
        A = self.A
        for state in A.states:
            self._check_state_label(state)

    def _check_one_initial_state(self):
        A = self.A
        if len(A.initial_states) == 0:
            raise RuntimeError('the automaton has no initial state')
        elif len(A.initial_states) > 1:
            raise RuntimeError('the automaton has multiple initial states')

    def _check_states_are_declared(self):
        A = self.A
        used_states = A.used_states()
        if len(used_states - A.states) > 0:
            raise RuntimeError('the following states are not declared: {}'.format(', '.join(used_states - A.states)))

    def _check_symbols_are_declared(self, used_symbols: Set[str], declared_symbols: Set[str]):
        if len(used_symbols - declared_symbols) > 0:
            raise RuntimeError('the following symbols are not declared: {}'.format(', '.join(used_symbols - declared_symbols)))

    def get_symbol(self, key: str, default_value: str) -> str:
        A = self.A
        if key in A.items:
            if len(A.items[key]) == 0:
                raise RuntimeError('no value was specified for "{}"'.format(key))
            if len(A.items[key]) > 1:
                print('A.items =', A.items)
                raise RuntimeError('multiple values were specified for "{}"'.format(key))
            return A.items[key][0]
        return default_value

    def parse_symbol(self, key='epsilon', value='ε', default_value='_'):
        A = self.A
        if key in A.items:
            return self.get_symbol(key, default_value)
        for (p, a, q) in A.transitions:
            if value in a:
                return value
        return default_value


    def get_symbol_set(self, key: str, used_symbols: Optional[Set[str]] = None) -> Set[str]:
        A = self.A
        if key in A.items:
            declared_symbols = set(A.items[key])
            if used_symbols:
                self._check_symbols_are_declared(used_symbols, declared_symbols)
            return declared_symbols
        return used_symbols

    def get_state(self, key: str, default_value: str) -> str:
        A = self.A
        if key in A.items:
            if len(A.items[key]) == 0:
                raise RuntimeError('no value was specified for "{}"'.format(key))
            if len(A.items[key]) > 1:
                raise RuntimeError('multiple values were specified for "{}"'.format(key))
            return A.items[key][0]
        return default_value

    def build(self) -> Automaton:
        A = self.A
        A.states = A.states if len(A.states) > 0 else A.used_states()
        self._check_states_are_declared()
        self._check_state_labels()
        return A


class AutomatonParser(object):
    def __init__(self, transition_regex=default_transition_label_regex(), state_regex=default_state_label_regex(), keywords: FrozenSet[str] = automaton_keywords()):
        self.keywords = keywords
        self.state_regex = state_regex
        self.transition_regex = transition_regex
        self.items = {}
        self.states: Set[str] = set([])
        self.transitions = []
        self.initial_states: Set[str] = set([])
        self.final_states: Set[str] = set([])

    def _check_no_duplicate_keys(self, key: str):
        if key in self.items:
            raise RuntimeError('the keyword "{}" is specified multiple times'.format(key))

    def _check_no_duplicates(self, words: List[str]) -> None:
        W = set([])
        for word in words:
            if word in W:
                raise RuntimeError('duplicate entry "{}" found in "{}"'.format(word, words))
            W.add(word)

    def _check_keys_exist(self, keys: List[str]):
        for key in keys:
            if not key in self.items:
                raise RuntimeError('the keyword "{}" is missing'.format(key))

    def _check_state_label(self, state) -> None:
        if not re.fullmatch(self.state_regex, state):
            raise RuntimeError('invalid state label {}'.format(state))

    def _check_transition_label(self, label) -> None:
        if not re.fullmatch(self.transition_regex, label):
            raise RuntimeError('invalid transition label {}'.format(label))

    def parse_state(self, state: str) -> str:
        self._check_state_label(state)
        return state

    def parse_state_set(self, keyword, words: List[str], check_non_empty: bool = False) -> Set[str]:
        self._check_no_duplicate_keys(keyword)
        self._check_no_duplicates(words)
        if check_non_empty and len(words) == 0:
            raise RuntimeError('the set "{}" may not be empty'.format(keyword))
        return set(self.parse_state(word) for word in words)

    def parse_transition_label(self, label: str) -> str:
        self._check_transition_label(label)
        return label

    def parse_transition(self, words: List[str], line: str):
        if len(words) <= 2:
            raise RuntimeError('incomplete transition "{}"'.format(line))
        p = self.parse_state(words[0])
        q = self.parse_state(words[1])
        for a in words[2:]:
            a = self.parse_transition_label(a)
            self.transitions.append((p, a, q))

    def parse_line(self, line: str):
        words = line.strip().split()
        if not words or words[0].startswith('%'):
            pass
        elif words[0] == 'states':
            self.states = self.parse_state_set('states', words[1:], check_non_empty=True)
            self.items['states'] = words[1:]
        elif words[0] == 'final':
            self.final_states = self.parse_state_set('final', words[1:])
            self.items['final'] = words[1:]
        elif words[0] == 'initial':
            self.initial_states = self.parse_state_set('initial', words[1:])
            self.items['initial'] = words[1:]
        elif words[0] in self.keywords:
            keyword = words[0]
            self._check_no_duplicate_keys(keyword)
            self.items[keyword] = words[1:]
        else:
            self.parse_transition(words, line)

    def parse(self, text: str) -> Automaton:
        lines = text.split('\n')
        for line in lines:
            self.parse_line(line)
        return Automaton(self.states, self.transitions, self.initial_states, self.final_states, self.items)


def parse_automaton(text: str, transition_regex=default_transition_label_regex(), state_regex=default_state_label_regex(), symbol_regex=default_symbol_regex()) -> Automaton:
    A = AutomatonParser(state_regex=state_regex, transition_regex=transition_regex).parse(text)
    return AutomatonBuilder(A, state_regex=state_regex, transition_regex=transition_regex, symbol_regex=symbol_regex).build()
