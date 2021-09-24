# Generated from CFG.g4 by ANTLR 4.8
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CFGParser import CFGParser
else:
    from CFGParser import CFGParser

# This class defines a complete generic visitor for a parse tree produced by CFGParser.

class CFGVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CFGParser#context_free_grammar.
    def visitContext_free_grammar(self, ctx:CFGParser.Context_free_grammarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CFGParser#rule_list.
    def visitRule_list(self, ctx:CFGParser.Rule_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CFGParser#symbol.
    def visitSymbol(self, ctx:CFGParser.SymbolContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CFGParser#variable.
    def visitVariable(self, ctx:CFGParser.VariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CFGParser#symbol_list.
    def visitSymbol_list(self, ctx:CFGParser.Symbol_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CFGParser#alternative.
    def visitAlternative(self, ctx:CFGParser.AlternativeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CFGParser#alternative_list.
    def visitAlternative_list(self, ctx:CFGParser.Alternative_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CFGParser#rule_.
    def visitRule_(self, ctx:CFGParser.Rule_Context):
        return self.visitChildren(ctx)



del CFGParser