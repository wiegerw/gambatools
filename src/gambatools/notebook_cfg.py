#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import re
from typing import Set, List, Union

from IPython.display import display, Markdown
from gambatools.cfg import Variable, Terminal, CFG, Rule
from gambatools.cfg_algorithms import parse_simple_cfg, cfg_cyk_matrix
from gambatools.notebook import print_feedback


def check_cyk_matrix(cfg: str, word: str, answer: str) -> None:
    def print_set(S: Set[str]) -> str:
        return '{' + ','.join(list(map(str, sorted(S)))) + '}'

    try:
        feedback = []
        G = parse_simple_cfg(cfg)
        Y = cfg_cyk_matrix(G, word)

        # check the syntax of the items
        lines = re.split('\n', answer.strip())
        for i, line in enumerate(lines):
            words = line.strip().split()
            for w in words:
                if w != '{}' and not re.fullmatch(r'{\w(,\w)*}', w):
                    feedback.append('Error: the entry {} is ill formed'.format(w))
                else:
                    variables = set(Variable(x) for x in re.sub(r'[{},]', '', w))
                    if not variables <= G.V:
                        feedback.append('Error: the entry {} contains unknown variables'.format(w))

        # check the sizes
        for i, line in enumerate(lines):
            words = line.strip().split()
            if len(words) != i + 1:
                feedback.append('Error: line {0} should contain {0} entries'.format(i + 1))

        # check the content; report at most one error
        lines = reversed(lines)
        n = len(word)
        for i, line in enumerate(lines):
            if feedback:
                break
            words = line.strip().split()
            for j, w in enumerate(words):
                expected_variables = Y[j, i+j]
                variables = set(Variable(x) for x in re.sub(r'[{},]', '', w))
                if variables != expected_variables:
                    feedback.append('Error: X[{},{}] has the wrong value {} instead of {}'.format(j+1, i+j+1, w, print_set(expected_variables)))
                    break

        print_feedback(feedback)
        if not feedback:
            accepted = G.S in Y[0, n - 1]
            markdown = 'The start variable {} is contained in $X_{{1n}}$, hence the word is {}accepted.'.format(G.S, '' if accepted else 'not ')
            display(Markdown(markdown))
            # print('The start variable {} is contained in X[1,{}], hence the word is {}accepted.'.format(G.S, n, '' if accepted else 'not '))
    except Exception as e:
        print('Error: {}'.format(e))


def cfg_apply_rule(G: CFG, rule: Rule, element: List[Union[Variable, Terminal]], derivation_type: str) -> List[List[Union[Variable, Terminal]]]:
    from gambatools.algorithms import last_index

    def apply(pos: int) -> List[Union[Variable, Terminal]]:
        return element[:pos] + rule.alternative.symbols + element[pos+1:]

    if rule.variable not in element:
        return []
    elif derivation_type == 'leftmost':
        pos = element.index(rule.variable)
        return [apply(pos)]
    elif derivation_type == 'rightmost':
        pos = last_index(element, rule.variable)
        return [apply(pos)]
    elif derivation_type == 'any':
        return [apply(pos) for pos, e in enumerate(element) if e == rule.variable]
    else:
        raise RuntimeError('unknown derivation type {}'.format(derivation_type))


# returns True if there is a derivation of the given type from elem1 to elem2
def cfg_has_derivation(G: CFG, elem1: List[Union[Variable, Terminal]], elem2: List[Union[Variable, Terminal]], derivation_type: str) -> bool:
    def find_variables() -> Set[Variable]:
        variables = [v for v in elem1 if isinstance(v, Variable)]
        if not variables:
            return set([])
        elif derivation_type == 'any':
            return set(variables)
        elif derivation_type == 'leftmost':
            return {variables[0]}
        elif derivation_type == 'rightmost':
            return {variables[-1]}
        else:
            raise RuntimeError('unknown derivation type {}'.format(derivation_type))

    R = G.R
    variables = find_variables()

    for rule in R:
        if rule.variable not in variables:
            continue
        if elem2 in cfg_apply_rule(G, rule, elem1, derivation_type):
            return True
    return False


def check_cfg_derivation(cfg: str, derivation: str, word: str, derivation_type='leftmost') -> None:
    def parse_character(c: str) -> Union[Variable, Terminal]:
        return Variable(c) if c.isupper() else Terminal(c)

    try:
        feedback = []
        G = parse_simple_cfg(cfg)
        V = G.V
        S = G.S
        Sigma = G.Sigma

        # parse the elements of the derivation
        words = derivation.strip().split('=>')
        words = [w.strip() for w in words]
        elements = [list(map(parse_character, element)) for element in words]

        if not elements:
            feedback.append('Error: the derivation is empty')

        # check if the elements correspond to the grammar
        for element in elements:
            for e in element:
                if (isinstance(e, Variable) and e not in V) or (isinstance(e, Terminal) and e not in Sigma):
                    feedback.append('Error: the element {} is invalid'.format(''.join(list(map(str, element)))))

        # check if the first element is the start symbol
        if elements:
            first = elements[0]
            if len(first) != 1 or first[0] != S:
                feedback.append('Error: the first element of the derivation must be the start variable of the grammar')

        # check if the steps are valid derivation steps
        msg = '' if derivation_type == 'any' else derivation_type + ' '
        for i in range(len(elements) - 1):
            if not cfg_has_derivation(G, elements[i], elements[i+1], derivation_type):
                feedback.append('Error: there is no {}derivation from {} to {}'.format(msg, words[i], words[i+1]))

        # check if the last element is equal to word
        if elements:
            last = elements[-1]
            if last != list(map(Terminal, word)):
                feedback.append('Error: the last element of the derivation must be equal to {}'.format(word))

        print_feedback(feedback)

    except Exception as e:
        print('Error: {}'.format(e))
