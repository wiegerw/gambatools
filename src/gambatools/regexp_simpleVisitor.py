# Generated from regexp_simple.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .regexp_simpleParser import regexp_simpleParser
else:
    from regexp_simpleParser import regexp_simpleParser

# This class defines a complete generic visitor for a parse tree produced by regexp_simpleParser.

class regexp_simpleVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by regexp_simpleParser#OneExpression.
    def visitOneExpression(self, ctx:regexp_simpleParser.OneExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexp_simpleParser#SymbolExpression.
    def visitSymbolExpression(self, ctx:regexp_simpleParser.SymbolExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexp_simpleParser#IterationExpression.
    def visitIterationExpression(self, ctx:regexp_simpleParser.IterationExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexp_simpleParser#ConcatExpression.
    def visitConcatExpression(self, ctx:regexp_simpleParser.ConcatExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexp_simpleParser#SumExpression.
    def visitSumExpression(self, ctx:regexp_simpleParser.SumExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexp_simpleParser#ZeroExpression.
    def visitZeroExpression(self, ctx:regexp_simpleParser.ZeroExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by regexp_simpleParser#ParensExpression.
    def visitParensExpression(self, ctx:regexp_simpleParser.ParensExpressionContext):
        return self.visitChildren(ctx)



del regexp_simpleParser