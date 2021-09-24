#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

#!/usr/bin/env python3

from gambatools.regexp import *
from gambatools.regexpParser import *
from gambatools.regexpVisitor import *
from gambatools.regexpLexer import *


def concatenation(expressions):
    if len(expressions) == 1:
        return expressions[0]
    return Concat(expressions[0], concatenation(expressions[1:]))


class regexpVisitor(regexpVisitor):

    def __init__(self):
        super(regexpVisitor, self).__init__()

    def make_unary_expression(self, unaryop, ctx):
        operand = self.visit(ctx.expression())
        return unaryop(operand)

    def make_binary_expression(self, binaryop, ctx):
        left = self.visit(ctx.expression(0))
        right = self.visit(ctx.expression(1))
        return binaryop(left, right)

    def visitOneExpression(self, ctx: regexpParser.OneExpressionContext):
        return One()

    def visitSymbolExpression(self, ctx: regexpParser.SymbolExpressionContext):
        return Symbol(ctx.getText())

    def visitIterationExpression(self, ctx: regexpParser.IterationExpressionContext):
        return self.make_unary_expression(Iteration, ctx)

    def visitConcatExpression(self, ctx: regexpParser.ConcatExpressionContext):
        return self.make_binary_expression(Concat, ctx)

    def visitSumExpression(self, ctx: regexpParser.SumExpressionContext):
        return self.make_binary_expression(Sum, ctx)

    def visitZeroExpression(self, ctx: regexpParser.ZeroExpressionContext):
        return Zero()

    def visitParensExpression(self, ctx: regexpParser.ParensExpressionContext):
        return self.visit(ctx.expression())


def parse_regexp(text):
    lexer = regexpLexer(InputStream(text))
    stream = CommonTokenStream(lexer)
    parser = regexpParser(stream)
    tree = parser.expression()
    visitor = regexpVisitor()
    return visitor.visit(tree)
