#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List, Set, Union
from collections import defaultdict


class Terminal(str):
    def __new__(cls, content):
        return super().__new__(cls, content)


class Variable(str):
    def __new__(cls, content):
        return super().__new__(cls, content)


DerivationTerm = List[Union[Terminal, Variable]]


class Alternative(object):
    def __init__(self, symbols: DerivationTerm):
        self.symbols = symbols

    def __str__(self):
        if not self.symbols:
            return 'ε'
        return '.'.join(self.symbols)

    def __eq__(self, other):
        return self.symbols == other.symbols

    def __hash__(self):
        return hash(str(self)) # TODO: improve this hash function

    def __lt__(self, other):
        return str(self) < str(other)

    def is_chomsky(self):
        """Returns true if the alternative is in Chomsky normal form"""
        return (len(self.symbols) == 0) or \
               (len(self.symbols) == 1 and isinstance(self.symbols[0], Terminal)) or \
               (len(self.symbols) == 2 and isinstance(self.symbols[0], Variable) and
                isinstance(self.symbols[1], Variable))

    def is_epsilon(self):
        return len(self.symbols) == 0

    def is_variable(self):
        return len(self.symbols) == 1 and isinstance(self.symbols[0], Variable)

    def is_terminal(self):
        return len(self.symbols) == 1 and isinstance(self.symbols[0], Terminal)

    def terminals(self) -> Set[Terminal]:
        """Returns the terminals of the alternative"""
        return set([symbol for symbol in self.symbols if isinstance(symbol, Terminal)])

    def variables(self) -> Set[Variable]:
        """Returns the variables of the alternative"""
        return set([symbol for symbol in self.symbols if isinstance(symbol, Variable)])


def cfg_equal_alternatives(a1: List[Alternative], a2: List[Alternative]) -> bool:
    symbols1 = [a.symbols for a in a1]
    symbols2 = [a.symbols for a in a2]
    return sorted(symbols1) == sorted(symbols2)


class Rule(object):
    def __init__(self, variable: Variable, alternative: Alternative):
        self.variable = variable
        self.alternative = alternative

    def __eq__(self, other):
        return self.variable == other.variable and self.alternative == other.alternative

    def __hash__(self):
        return hash(str(self)) # TODO: improve this hash function

    def is_chomsky(self):
        """Returns true if the rule is in Chomsky normal form"""
        return self.alternative.is_chomsky()

    def is_epsilon(self):
        return self.alternative.is_epsilon()

    def is_unit_rule(self):
        return self.alternative.is_variable()

    def terminals(self) -> Set[Terminal]:
        return self.alternative.terminals()

    def variables(self) -> Set[Variable]:
        return self.alternative.variables()

    def __str__(self):
        return '{} -> {}'.format(self.variable, self.alternative)


class CFG(object):

    def __init__(self, V: Set[Variable], Sigma: Set[Terminal], R: List[Rule], S: Variable, epsilon: Terminal = Terminal('ε'), check_validity: bool = True):
        self.V = V
        self.Sigma = Sigma
        self.R = R
        self.S = S
        self.epsilon = epsilon
        if check_validity:
            self.check_validity()

    def ordered_variables(self):
        """Returns the variables in the order of first appearance in R"""
        done = set([])
        result = []
        for rule in self.R:
            if rule.variable not in done:
                done.add(rule.variable)
                result.append(rule.variable)
        return result

    def __str__(self):
        rule_map = defaultdict(lambda: [])
        for rule in self.R:
            rule_map[rule.variable].append(rule.alternative)
        rules = ['{} -> {}'.format(X, ' | '.join(list(map(str, rule_map[X])))) for X in self.ordered_variables()]
        return '\n'.join(rules)

    def __eq__(self, other):
        return self.V == other.V and \
               self.Sigma == other.Sigma and \
               self.S == other.S and \
               sorted(map(str, self.R)) == sorted(map(str, other.R))

    def is_valid(self):
        V = self.V
        Sigma = self.Sigma
        R = self.R
        S = self.S
        # for rule in R:
        #     if not rule.variables() <= V:
        #         print('V1', V, rule.variables() - V)
        #     if not rule.terminals() <= Sigma:
        #         print('V2', Sigma, rule.terminals() - Sigma)
        #     if not rule.variable in V:
        #         print('V3', V, rule.variable)
        return all([rule.variables() <= V for rule in self.R]) \
               and all([rule.terminals() <= Sigma for rule in self.R]) \
               and all([rule.variable in V for rule in self.R])
               # and len(set([rule.variable for rule in self.R])) == len(self.R)

    def check_validity(self):
        V = self.V
        Sigma = self.Sigma
        R = self.R
        S = self.S
        for rule in R:
            if not rule.variables() <= V:
                undeclared_variables = rule.variables() - V
                raise RuntimeError('the rule {} contains undeclared variables {}'.format(rule, *undeclared_variables))
            if not rule.terminals() <= Sigma:
                undeclared_terminals = rule.terminals() - Sigma
                raise RuntimeError('the rule {} contains undeclared terminals {}'.format(rule, *undeclared_terminals))
            if not rule.variable in V:
                raise RuntimeError('the rule {} contains undeclared variable {}'.format(rule, rule.variable))
        return all([rule.variables() <= V for rule in self.R]) \
               and all([rule.terminals() <= Sigma for rule in self.R]) \
               and all([rule.variable in V for rule in self.R])
               # and len(set([rule.variable for rule in self.R])) == len(self.R)

    def is_chomsky(self):
        """Returns true if the grammar is in Chomsky normal form"""
        return all([rule.is_chomsky() and self.S not in rule.variables() for rule in self.R]) and \
               all([not rule.is_epsilon() or rule.variable == self.S for rule in self.R])
