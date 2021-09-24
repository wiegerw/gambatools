# Generated from regexp.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .regexpParser import regexpParser
else:
    from regexpParser import regexpParser

# This class defines a complete generic visitor for a parse tree produced by regexpParser.

class regexpVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by regexpParser#OneExpression.
    def visitOneExpression(self, ctx:regexpParser.OneExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexpParser#SymbolExpression.
    def visitSymbolExpression(self, ctx:regexpParser.SymbolExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexpParser#IterationExpression.
    def visitIterationExpression(self, ctx:regexpParser.IterationExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexpParser#ConcatExpression.
    def visitConcatExpression(self, ctx:regexpParser.ConcatExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexpParser#SumExpression.
    def visitSumExpression(self, ctx:regexpParser.SumExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexpParser#ZeroExpression.
    def visitZeroExpression(self, ctx:regexpParser.ZeroExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexpParser#ParensExpression.
    def visitParensExpression(self, ctx:regexpParser.ParensExpressionContext):
        return self.visitChildren(ctx)



del regexpParser