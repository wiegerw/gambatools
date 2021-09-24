#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import copy
import itertools
import re
import string
from collections import defaultdict
from typing import List, Set, MutableMapping, Tuple, Union, Optional, DefaultDict

from gambatools.algorithms import last_index, first_index
from gambatools.dfa import State, Symbol, DFA
from gambatools.nfa import NFA
from gambatools.cfg import CFG, Terminal, Variable, Alternative, Rule, DerivationTerm
from gambatools.list_utility import remove_none, remove_duplicates, remove_if


class BaetenCFGParser(object):

    @staticmethod
    def is_comment(line: str):
        return line.strip().startswith('#')

    @staticmethod
    def parse_variable(ch: str) -> Union[Terminal, Variable]:
        return Terminal(ch) if ch.islower() else Variable(ch)

    def parse_alternative(self, text: str) -> Optional[Alternative]:
        if text == '0':
            return None
        elif text == '1':
            return Alternative([])
        return Alternative([self.parse_variable(ch) for ch in text])

    def parse_rule(self, text: str) -> List[Rule]:
        if self.is_comment(text):
            return []
        words = list(filter(None, re.split(r'\s+', text)))
        if len(words) < 2:
            return []
        lhs = Variable(words[0])
        alternatives = remove_none([self.parse_alternative(alternative) for alternative in words[1:]])
        return [Rule(lhs, alternative) for alternative in alternatives]

    def parse_grammar(self, text: str, check_validity: bool = True):
        text = re.sub('[=+]', '', text)
        R = list(itertools.chain.from_iterable(self.parse_rule(line) for line in text.split('\n')))
        V = set([rule.variable for rule in R])
        Sigma = set().union(*[rule.terminals() for rule in R])
        S = R[0].variable
        return CFG(V, Sigma, R, S, check_validity=check_validity)


class SimpleCFGParser(object):
    def __init__(self):
        def repeat(x):
            return '(' + x + r')*'
        self.epsilon = None
        self.zero = '@'
        self.alternative_regex = r'[\.\w]+'
        self.variable_regex = r'\w+'
        S = r'\s*'
        A = self.alternative_regex
        V = self.variable_regex
        bar = r'\|'
        self.rule_regex = S + V + S + '->' + S + A + repeat(S + bar + S + A + S)

    @staticmethod
    def is_comment(line: str):
        return line.strip().startswith('%')

    @staticmethod
    def parse_variable(ch: str) -> Union[Terminal, Variable]:
        return Terminal(ch) if ch.islower() else Variable(ch)

    def parse_alternative(self, text: str) -> Optional[Alternative]:
        if text == self.zero:
            return None
        elif text == self.epsilon:
            return Alternative([])
        return Alternative([self.parse_variable(ch) for ch in text])

    def parse_rule(self, line: str) -> List[Rule]:
        words = re.split(r'->', line)
        if len(words) != 2:
            raise RuntimeError('invalid production {}'.format(line))
        lhs = Variable(words[0].strip())
        alternatives = words[1].strip().split('|')
        alternatives = remove_none([self.parse_alternative(alternative.strip()) for alternative in alternatives])
        return [Rule(lhs, alternative) for alternative in alternatives]

    def parse_epsilon(self, lines):
        result = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('%'):
                pass
            elif line.startswith('epsilon'):
                m = re.fullmatch(r'epsilon\s*=\s*(\w)', line)
                if not m:
                    raise RuntimeError('invalid epsilon declaration {}'.format(line))
                self.epsilon = m.group(1)
            else:
                if re.fullmatch(self.rule_regex, line):
                    result.append(line)
                else:
                    raise RuntimeError('invalid production {}'.format(line))
        if not self.epsilon:
            self.epsilon = 'ε' if any(['ε' in line for line in result]) else '_'
        return result

    def parse_grammar(self, text: str, check_validity: bool = True):
        lines = text.split('\n')
        lines = self.parse_epsilon(lines)
        R = list(itertools.chain.from_iterable(self.parse_rule(line) for line in lines))
        if not R:
            raise RuntimeError('the grammar has no rules')
        V = set([rule.variable for rule in R])
        Sigma = set().union(*[rule.terminals() for rule in R])
        S = R[0].variable
        return CFG(V, Sigma, R, S, epsilon=Terminal(self.epsilon), check_validity=check_validity)


def parse_cfg_baeten(text: str, check_validity: bool = True) -> CFG:
    """
    Parse a CFG in the format used by Baeten:

    S = aA + bB
    A = a + B
    B = b + 1

    Variables are upper case, 1 is the empty string.
    :param text: a string containing a grammar
    :param check_validity:
    :return: the grammar
    """

    parser = BaetenCFGParser()
    return parser.parse_grammar(text, check_validity)


def parse_simple_cfg(text: str, check_validity: bool = True) -> CFG:
    """
    Parse a CFG in a format used by Sipser:

    S -> aA | bB
    A -> a | B
    B -> b | _

    Variables are upper case, _ is the empty string.
    :param text: a string containing a grammar
    :param check_validity:
    :return: the grammar
    """

    parser = SimpleCFGParser()
    return parser.parse_grammar(text, check_validity)


def cfg_to_dfa(G: CFG, check_validity: bool = True) -> DFA:
    def is_epsilon(alternative: Alternative):
        return len(alternative.symbols) == 0 or (len(alternative.symbols) == 1 and alternative.symbols[0] == G.epsilon)

    def is_transition(alternative: Alternative) -> bool:
        return len(alternative.symbols) == 2 and isinstance(alternative.symbols[0], Terminal) and isinstance(alternative.symbols[1], Variable)

    Sigma: Set[Symbol] = set([Symbol(t) for t in G.Sigma])
    Q: Set[State] = set([State(t) for t in G.V])
    delta: MutableMapping[Tuple[State, Symbol], State] = {}
    F: Set[State] = set([])
    q0: State = next(q for q in Q if q == State(G.S))

    for rule in G.R:
        q = State(rule.variable)
        if is_epsilon(rule.alternative):
            F.add(q)
        elif is_transition(rule.alternative):
            a = Symbol(rule.alternative.symbols[0])
            q1 = State(rule.alternative.symbols[1])
            delta[q, a] = q1
        else:
            raise RuntimeError('cga2nfa: alternative {} has the wrong format'.format(rule.alternative))
    return DFA(Q, Sigma, delta, q0, F, check_validity=check_validity)


def cfg_to_nfa(grammar: CFG) -> NFA:
    """Transforms a CFG to an NFA. The CFG must already be in the right format."""
    def is_epsilon(alternative: Alternative):
        return len(alternative.symbols) == 0 or (len(alternative.symbols) == 1 and alternative.symbols[0] == grammar.epsilon)

    def is_epsilon_transition(alternative: Alternative) -> bool:
        return len(alternative.symbols) == 1 and isinstance(alternative.symbols[0], Variable)

    def is_transition(alternative: Alternative) -> bool:
        return len(alternative.symbols) == 2 and isinstance(alternative.symbols[0], Terminal) and isinstance(alternative.symbols[1], Variable)

    Sigma: Set[Symbol] = set([Symbol(t) for t in grammar.Sigma])
    Q: Set[State] = set([State(t) for t in grammar.V])
    delta = defaultdict(lambda: set([]))  # delta: TypedDict[Tuple[State, Symbol], Set[State]]
    F: Set[State] = set([])
    q0: State = next(q for q in Q if q == State(grammar.S))
    epsilon = Symbol('')

    for rule in grammar.R:
        q = State(rule.variable)
        if is_epsilon(rule.alternative):
            F.add(q)
        elif is_epsilon_transition(rule.alternative):
            q1 = State(rule.alternative.symbols[0])
            delta[q, epsilon].add(q1)
        elif is_transition(rule.alternative):
            a = Symbol(rule.alternative.symbols[0])
            q1 = State(rule.alternative.symbols[1])
            delta[q, a].add(q1)
        else:
            raise RuntimeError('cga2nfa: alternative {} has the wrong format'.format(rule.alternative))
    return NFA(Q, Sigma, delta, q0, F, epsilon)


def expand_nullable_variables(x: DerivationTerm, W: Set[Variable]) -> List[DerivationTerm]:
    """Expands nullable variables (elements in W) in x."""
    if len(x) == 0:
        return [x]
    y = expand_nullable_variables(x[1:], W)
    result = [[x[0]] + y_i for y_i in y]
    if isinstance(x[0], Variable) and x[0] in W:
        result = result + y
    return result


def cfg_nullable_variables(G: CFG) -> Set[Variable]:
    R = G.R
    nullable = set([])

    while True:
        changed = False
        for r in R:
            if r.variable not in nullable and all(x in nullable for x in r.alternative.symbols):
                nullable.add(r.variable)
                changed = True
        if not changed:
            break

    return nullable


def cfg_remove_epsilon_rules_in_place(G: CFG) -> None:
    R = G.R
    S = G.S

    W = cfg_nullable_variables(G)

    # R1 contains the new list of rules
    R1 = []

    for rule in R:
        for symbols in expand_nullable_variables(rule.alternative.symbols, W):
            if not symbols and rule.variable in W - {S}:
                continue
            R1.append(Rule(rule.variable, Alternative(symbols)))

    R1 = remove_duplicates(R1)
    R.clear()
    R.extend(R1)


def cfg_remove_epsilon_rules(G: CFG) -> CFG:
    G = copy.deepcopy(G)
    cfg_remove_epsilon_rules_in_place(G)
    return G


def cfg_derivable_variables(G: CFG, A: Variable) -> Set[Variable]:
    R = G.R
    V = G.V

    W: Set[Variable] = set([])
    W1: Set[Variable] = set([])

    for r in R:
        if r.variable == A and len(r.alternative.symbols) == 1:
            B = r.alternative.symbols[0]
            if B in V:
                W.add(B)

    while W1 != W:
        W1 = W.copy()
        for r in R:
            if len(r.alternative.symbols) == 1:
                C = r.variable
                B = r.alternative.symbols[0]
                if C in W1 and B in V:
                    W.add(B)
    return W - {A}


def cfg_put_start_variable_in_front(G: CFG) -> None:
    R = G.R
    S = G.S
    for i in range(len(R)):
        if R[i].variable == S:
            R[0], R[i] = R[i], R[0]
            break


def cfg_eliminate_unit_rules_in_place(G: CFG) -> None:
    R = G.R
    V = G.V
    R1 = R.copy()

    for A in V:
        W = cfg_derivable_variables(G, A)
        for r in R:
            B = r.variable
            if B in W and not r.is_unit_rule():
                alpha = r.alternative
                r1 = Rule(A, alpha)
                if not r1 in R1:
                    R1.append(r1)
    R1 = remove_if(R1, lambda x: x.is_unit_rule())
    G.R = R1
    cfg_put_start_variable_in_front(G)


def cfg_eliminate_unit_rules(G: CFG) -> CFG:
    G = copy.deepcopy(G)
    cfg_eliminate_unit_rules_in_place(G)
    return G


def cfg_fresh_variable(G: CFG, hint: str) -> Variable:
    # assert len(hint) == 1
    # assert hint.isupper()

    V = G.V
    if len(V) >= 26:
        index = 0
        A = Variable(hint)
        while A in V:
            A = Variable('{}{}'.format(hint, index))
            index = index + 1
        return A
    else:
        if Variable(hint) not in V:
            A = Variable(hint)
            return A
        for A in string.ascii_uppercase:
            if Variable(A) not in V:
                A = Variable(A)
                return A


def cfg_add_new_start_variable_in_place(G: CFG, hint: str = 'S') -> None:
    S0 = cfg_fresh_variable(G, hint)
    G.R.insert(0, Rule(S0, Alternative([G.S])))
    G.V.add(S0)
    G.S = S0


def cfg_add_new_start_variable(G: CFG, hint: str = 'S') -> CFG:
    G = copy.deepcopy(G)
    cfg_add_new_start_variable_in_place(G, hint)
    return G


def cfg_make_rules_of_length_two_in_place(G: CFG) -> None:
    def fresh_variables(hint: str, n: int) -> List[Variable]:
        """Returns n fresh variables and adds them to G.V"""
        result = []
        index = 0
        for i in range(n):
            P = cfg_fresh_variable(G, hint)
            result.append(P)
            G.V.add(P)
        return result

    for rule in G.R.copy():
        A = rule.variable
        a = rule.alternative
        u = a.symbols
        n = len(u)
        if n <= 2:
            continue
        A = fresh_variables(A, n - 2)
        for k in range(n - 3):
            G.R.append(Rule(A[k], Alternative([u[k + 1], A[k + 1]])))
        G.R.append(Rule(A[-1], Alternative(u[-2:])))
        a.symbols = [u[0], A[0]]


def cfg_make_rules_of_length_two(G: CFG) -> CFG:
    G = copy.deepcopy(G)
    cfg_make_rules_of_length_two_in_place(G)
    return G


def cfg_eliminate_terminals_in_place(G: CFG) -> None:
    replacements: MutableMapping[Terminal, Variable] = {}

    def replace_symbol(symbol: Union[Variable, Terminal]) -> Variable:
        if isinstance(symbol, Terminal):
            if symbol not in replacements:
                A = cfg_fresh_variable(G, symbol.upper())
                replacements[symbol] = A
                G.V.add(A)
            return replacements[symbol]
        else:
            return symbol

    for rule in G.R:
        a = rule.alternative
        if len(a.symbols) >= 2:
            a.symbols = [replace_symbol(symbol) for symbol in a.symbols]

    for terminal, variable in replacements.items():
        A = variable
        a = Alternative([terminal])
        G.R.append(Rule(A, a))


def cfg_eliminate_terminals(G: CFG) -> CFG:
    G = copy.deepcopy(G)
    cfg_eliminate_terminals_in_place(G)
    return G


def cfg_to_chomsky_in_place(G: CFG, verbose: bool = False) -> None:
    if verbose: print('--- start ---\n', G, ' V =', *G.V)
    cfg_add_new_start_variable_in_place(G)
    if verbose: print('--- cfg_add_new_start_variable_in_place ---\n', G, '\n variables =', *G.V)
    cfg_remove_epsilon_rules_in_place(G)
    if verbose: print('--- cfg_remove_epsilon_rules_in_place ---\n', G, '\n variables =', *G.V)
    cfg_eliminate_unit_rules_in_place(G)
    if verbose: print('--- cfg_eliminate_unit_rules_in_place ---\n', G, '\n variables =', *G.V)
    cfg_make_rules_of_length_two_in_place(G)
    if verbose: print('--- cfg_make_rules_of_length_two_in_place ---\n', G, '\n variables =', *G.V)
    cfg_eliminate_terminals_in_place(G)
    if verbose: print('--- cfg_eliminate_terminals_in_place ---\n', G, '\n variables =', *G.V)


def cfg_to_chomsky(G: CFG, verbose: bool = False) -> CFG:
    G = copy.deepcopy(G)
    cfg_to_chomsky_in_place(G, verbose)
    return G


def cfg_cyk_matrix(G: CFG, w: str, verbose: bool = False) -> DefaultDict[Tuple[int, int], Set[Variable]]:
    assert G.is_chomsky()

    V = G.V
    R = G.R
    n = len(w)

    # Build a mapping P of all productions
    P = defaultdict(lambda: [])
    for rule in R:
        P[rule.variable].append(rule.alternative.symbols)

    # X[i, j] will contain { A | A -> w[i].w[i+1]...w[j] }
    X = defaultdict(lambda: set([]))
    for i in range(n):
        w_i = [Terminal(w[i])]
        X[i, i] = set(A for A in V if w_i in P[A])

    if verbose:
        print('--- start ---')
        print('V = ', *V)
        for i, j in X:
            print('X[{}, {}] = {}'.format(i, j, X[i, j]))

    for m in range(1, n):
        for i in range(n - m):
            j = i + m
            if verbose: print('processing X[{}, {}]'.format(i, j))
            for k in range(i, j):
                if verbose: print('X[{}, {}] depends on X[{}, {}] and X[{}, {}]'.format(i, j, i, k, k + 1, j))
                for (B, C) in itertools.product(X[i, k], X[k + 1, j]):
                    if verbose: print('B, C = ', B, C)
                    X[i, j] |= set(A for A in V if [B, C] in P[A])
                    if verbose: print('===> X[{}, {}] = {}'.format(i, j, X[i, j]))

    if verbose:
        print('--- end ---')
        for i, j in X:
            print('X[{}, {}] = {}'.format(i, j, X[i, j]))

    return X


def cfg_print_cyk_matrix(X: DefaultDict[Tuple[int, int], Set[Variable]], n: int) -> str:
    def print_set(S: Set[str]) -> str:
        return '{' + ','.join(list(map(str, sorted(S)))) + '}'

    width = (max(len(V) for _, V in X.items()) * 2) + 1
    lines = []
    for i in range(n):
        line = '  '.join("{:<{width}}".format(print_set(X[j-i, j]), width=width) for j in range(i, n))
        # line = '  '.join('X[{},{}]'.format(j-i, j) for j in range(i, n))
        lines.append(line)
    return '\n'.join(reversed(lines))


def cfg_accepts_word(G: CFG, w: str, verbose: bool = False) -> bool:
    """Uses the CYK algorithm to determine if w is in L(G)"""

    if not G.is_chomsky():
        G = cfg_to_chomsky(G)
        if verbose:
            print('grammar converted to Chomsky:')
            print(G)

    R = G.R
    S = G.S

    if w == '':
        return Rule(S, Alternative([])) in R

    X = cfg_cyk_matrix(G, w, verbose)
    n = len(w)
    return S in X[0, n - 1]


# Returns a derivation of the word w
def cfg_derive_word(G: CFG, w: str, derivation_type: str = 'any') -> DerivationTerm:
    assert G.is_chomsky()
    assert derivation_type in ['any', 'leftmost', 'rightmost']

    def find_rule(rules, Xpm, Xmq):
        for BC in rules:
            B, C = BC
            if B in Xpm and C in Xmq:
                return B, C
        return None

    def print_derivation_tree(root):
        S, p, q, children = root
        for child in children:
            print_derivation_tree(child)

    def extract_derivation(root, leftmost: bool):
        S = root[0]
        element = [S]
        result = [element]
        todo = [root]
        while todo:
            A, p, q, children = todo.pop(0) if leftmost else todo.pop()
            if children:
                value = [child[0] for child in children]
                pos = first_index(element, A) if leftmost else last_index(element, A)
                element = element[:pos] + value + element[pos+1:]
                result.append(element)
                if leftmost:
                    todo = children + todo
                else:
                    todo = todo + children
        return result

    R = G.R
    S = G.S

    X = cfg_cyk_matrix(G, w)
    n = len(w)
    if S not in X[0, n - 1]:
        raise RuntimeError("the word '{}' is not accepted by the grammar".format(w))

    # Build a mappings P1 and P2 for productions of length 1 and 2
    P = defaultdict(lambda: [])
    for rule in R:
        P[rule.variable].append(rule.alternative.symbols)

    root = (S, 0, n, [])
    todo = [ root ]
    while todo:
        A, p, q, children = todo.pop()
        if q - p == 1:
            a = w[p]
            child = (a, p, q, [])
            children.append(child)
        else:
            for m in range(p+1, q):
                Xpm = X[p, m-1]
                Xmq = X[m, q-1]
                BC = find_rule(P[A], Xpm, Xmq)
                if not BC:
                    continue
                B, C = BC
                child1 = (B, p, m, [])
                child2 = (C, m, q, [])
                children.append(child1)
                children.append(child2)
                todo.append(child1)
                todo.append(child2)
                break

    # print_derivation_tree(root)
    return extract_derivation(root, derivation_type in ['any', 'leftmost'])


def cfg_words_up_to_n(G: CFG, n: int) -> Set[str]:
    if not G.is_chomsky():
        G = cfg_to_chomsky(G)
    S = G.S
    R = G.R

    words = set([])

    S_empty = Rule(S, Alternative([]))
    if S_empty in R:
        words.add('')

    R1: DefaultDict[Variable, List[Symbol]] = defaultdict(lambda: [])
    R2: DefaultDict[Variable, List[DerivationTerm]] = defaultdict(lambda: [])
    for rule in R:
        if len(rule.alternative.symbols) == 1:
            R1[rule.variable].append(rule.alternative.symbols[0])
        elif len(rule.alternative.symbols) == 2:
            R2[rule.variable].append(rule.alternative.symbols)

    # pre: x.isupper() and len(x) > 0
    # replaces variables by symbols
    def make_words(x: DerivationTerm) -> Set[str]:
        if len(x) == 1:
            return set(R1[x[0]])
        words = make_words(x[1:])
        return set([a + word for a in R1[x[0]] for word in words])

    # pre: x.isupper()
    # replaces one variable by its right hand side
    def replace(x: DerivationTerm) -> List[DerivationTerm]:
        return [x[:j] + rhs + x[j+1:] for j in range(len(x)) for rhs in R2[x[j]]]

    def remove_duplicates(x: list) -> list:
        x.sort()
        return list(k for k, _ in itertools.groupby(x))

    W: List[DerivationTerm] = [[G.S]]
    words = words | make_words([G.S])

    for i in range(2, n + 1):
        W = remove_duplicates([x for word in W for x in replace(word)])
        words = words.union(*[make_words(word) for word in W])

    return words


def cfg_is_simple(G: CFG) -> bool:
    def is_simple_variable(x: str):
        return len(x) == 1 and x.isupper()

    def is_simple_symbol(x: str):
        return len(x) == 1 and x.islower()

    return all(is_simple_variable(x) for x in G.V) and all(is_simple_symbol(x) for x in G.Sigma)


def cfg_productive_variables(G: CFG) -> Set[Variable]:
    productive = set([])

    def is_productive_symbol(x: Union[Variable, Terminal]) -> bool:
        return isinstance(x, Terminal) or x in productive

    while True:
        changed = False
        for r in G.R:
            if r.variable not in productive and all(is_productive_symbol(x) for x in r.alternative.symbols):
                productive.add(r.variable)
                changed = True
        if not changed:
            break
    return productive


def cfg_remove_inproductive_variables_in_place(G: CFG) -> None:
    from gambatools.list_utility import remove_if

    productive = cfg_productive_variables(G)

    def is_productive_symbol(x: Union[Variable, Terminal]) -> bool:
        return isinstance(x, Terminal) or x in productive

    def is_productive(r: Rule) -> bool:
        return r.variable in productive and all(is_productive_symbol(x) for x in r.alternative.symbols)

    remove_if(G.R, lambda r: not is_productive(r))
    G.V &= productive


def cfg_remove_inproductive_variables(G: CFG) -> CFG:
    G = copy.deepcopy(G)
    cfg_remove_inproductive_variables_in_place(G)
    return G


def cfg_remove_useless_rules_in_place(G: CFG) -> None:
    from gambatools.list_utility import remove_if

    def is_useless(r: Rule) -> bool:
        return r.alternative.symbols == [r.variable]

    remove_if(G.R, lambda r: is_useless(r))


def cfg_remove_useless_rules(G: CFG) -> CFG:
    G = copy.deepcopy(G)
    cfg_remove_useless_rules_in_place(G)
    return G


def cfg_print_simple(G):
    if not cfg_is_simple(G):
        raise RuntimeError('the CFG is not in simple format')

    def print_alternative(a: Alternative) -> str:
        if not a.symbols:
            return 'ε'
        return ''.join(a.symbols)

    rule_map = defaultdict(lambda: [])
    for rule in G.R:
        rule_map[rule.variable].append(rule.alternative)
    rules = ['{} -> {}'.format(X, ' | '.join(list(map(print_alternative, rule_map[X])))) for X in G.ordered_variables()]
    return '\n'.join(rules)
