#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

#!/usr/bin/env python3

from gambatools.regexp import *
from gambatools.regexp_simpleParser import *
from gambatools.regexp_simpleVisitor import *
from gambatools.regexp_simpleLexer import *


def concatenation(expressions):
    if len(expressions) == 1:
        return expressions[0]
    return Concat(expressions[0], concatenation(expressions[1:]))


class regexp_simpleVisitor(regexp_simpleVisitor):

    def __init__(self, simple = False):
        super(regexp_simpleVisitor, self).__init__()
        self.simple = simple

    def make_unary_expression(self, unaryop, ctx):
        operand = self.visit(ctx.expression())
        return unaryop(operand)

    def make_binary_expression(self, binaryop, ctx):
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return binaryop(left, right)

    def visitOneExpression(self, ctx: regexp_simpleParser.OneExpressionContext):
        return One()

    def visitSymbolExpression(self, ctx: regexp_simpleParser.SymbolExpressionContext):
        return Symbol(ctx.getText())

    def visitIterationExpression(self, ctx: regexp_simpleParser.IterationExpressionContext):
        return self.make_unary_expression(Iteration, ctx)

    def visitConcatExpression(self, ctx: regexp_simpleParser.ConcatExpressionContext):
        return self.make_binary_expression(Concat, ctx)

    def visitSumExpression(self, ctx: regexp_simpleParser.SumExpressionContext):
        return self.make_binary_expression(Sum, ctx)

    def visitZeroExpression(self, ctx: regexp_simpleParser.ZeroExpressionContext):
        return Zero()

    def visitParensExpression(self, ctx: regexp_simpleParser.ParensExpressionContext):
        return self.visit(ctx.expression())


def parse_simple_regexp(text):
    lexer = regexp_simpleLexer(InputStream(text))
    stream = CommonTokenStream(lexer)
    parser = regexp_simpleParser(stream)
    tree = parser.expression()
    visitor = regexp_simpleVisitor()
    return visitor.visit(tree)
