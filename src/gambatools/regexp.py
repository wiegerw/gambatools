#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Union, Tuple


class Regexp(object):
    pass


class Zero(Regexp):
    def __str__(self):
        return '0'


class One(Regexp):
    def __str__(self):
        return '1'


class Symbol(Regexp):
    def __init__(self, symbol: str):
        self.symbol = symbol

    def __str__(self):
        return self.symbol


class Iteration(Regexp):
    def __init__(self, operand: Regexp):
        self.operand = operand

    def __str__(self):
        return print_unary_right_operation(self, '*')


class Sum(Regexp):
    def __init__(self, left: Regexp, right: Regexp):
        self.left = left
        self.right = right

    def __str__(self):
        return print_binary_operation(self, ' + ')


class Concat(Regexp):
    def __init__(self, left: Regexp, right: Regexp):
        self.left = left
        self.right = right

    def __str__(self):
        return print_binary_operation(self, ' . ')


def precedence(r: Regexp) -> int:
    if isinstance(r, (Zero, One, Symbol)):
        return 10
    elif isinstance(r, Iteration):
        return 9
    elif isinstance(r, Concat):
        return 8
    elif isinstance(r, Sum):
        return 7
    else:
        raise RuntimeError('precedence: unknown expression {}: {}'.format(r, r.__class__))


def is_left_associative(r: Union[Concat, Sum]):
    return True


def is_right_associative(r: Union[Concat, Sum]):
    return True


def print_expression(x: Regexp, needs_parentheses: bool) -> str:
    if needs_parentheses:
        return '({})'.format(x)
    return '{}'.format(x)


def print_unary_operand(x: Iteration, operand: Regexp) -> str:
    return print_expression(operand, precedence(operand) < precedence(x))


def print_unary_left_operation(x: Iteration, op: str) -> str:
    return '{}{}'.format(op, print_unary_operand(x, x.operand))


def print_unary_right_operation(x: Iteration, op: str) -> str:
    return '{}{}'.format(print_unary_operand(x, x.operand), op)


def print_binary_operation(x: Union[Concat, Sum], op: str) -> str:
    x1 = x.left
    x2 = x.right
    p = precedence(x)
    p1 = precedence(x1)
    p2 = precedence(x2)
    return '{}{}{}'.format(
        print_expression(x1, (p1 < p) or (p1 == p and not is_left_associative(x))),
        op,
        print_expression(x2, (p2 < p) or (p2 == p and not is_right_associative(x)))
    )


def print_regexp(x: Regexp) -> str:
    if isinstance(x, Zero):
        return '0'
    elif isinstance(x, One):
        return '1'
    elif isinstance(x, Symbol):
        return x.symbol
    elif isinstance(x, Iteration):
        return '({})*'.format(print_regexp(x.operand))
    elif isinstance(x, Sum):
        return '({} + {})'.format(print_regexp(x.left), print_regexp(x.right))
    elif isinstance(x, Concat):
        return '({} . {})'.format(print_regexp(x.left), print_regexp(x.right))


def print_regexp_simple(x: Regexp) -> str:
    def needs_parentheses_unary(x: Iteration) -> bool:
        return precedence(x.operand) < precedence(x)

    def needs_parentheses_binary(x: Union[Concat, Sum]) -> Tuple[bool, bool]:
        x1 = x.left
        x2 = x.right
        p = precedence(x)
        p1 = precedence(x1)
        p2 = precedence(x2)
        return (p1 < p) or (p1 == p and not is_left_associative(x)), (p2 < p) or (
                    p2 == p and not is_right_associative(x))

    if isinstance(x, Zero):
        return '0'
    elif isinstance(x, One):
        return '1'
    elif isinstance(x, Symbol):
        return x.symbol
    elif isinstance(x, Iteration):
        if needs_parentheses_unary(x):
            return '({})*'.format(print_regexp_simple(x.operand))
        else:
            return '{}*'.format(print_regexp_simple(x.operand))
    elif isinstance(x, Sum):
        n1, n2 = needs_parentheses_binary(x)
        x1 = print_regexp_simple(x.left)
        x2 = print_regexp_simple(x.right)
        if n1:
            x1 = '({})'.format(x1)
        if n2:
            x2 = '({})'.format(x2)
        return '{}+{}'.format(x1, x2)
    elif isinstance(x, Concat):
        n1, n2 = needs_parentheses_binary(x)
        x1 = print_regexp_simple(x.left)
        x2 = print_regexp_simple(x.right)
        if n1:
            x1 = '({})'.format(x1)
        if n2:
            x2 = '({})'.format(x2)
        return '{}{}'.format(x1, x2)
