#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

#!/usr/bin/env python3

from gambatools.CFGLexer import *
from gambatools.CFGVisitor import *
from gambatools.CFGParser import *
from gambatools.cfg import *
from gambatools.list_utility import remove_none


class CFGVisitor(CFGVisitor):

    def __init__(self):
        super(CFGVisitor, self).__init__()

    def visitContext_free_grammar(self, ctx: CFGParser.Context_free_grammarContext):
        return self.visit(ctx.rule_list())

    def visitRule_(self, ctx: CFGParser.Rule_Context):
        variable = self.visit(ctx.variable())
        alternatives = self.visit(ctx.alternative_list())
        return (variable, alternatives)

    def visitRule_list(self, ctx: CFGParser.Rule_listContext):
        return remove_none([self.visit(child) for child in ctx.children])

    def visitSymbol(self, ctx: CFGParser.SymbolContext):
        text = ctx.getText()
        return text

    def visitSymbol_list(self, ctx: CFGParser.Symbol_listContext):
        return remove_none([self.visit(child) for child in ctx.children])

    def visitVariable(self, ctx: CFGParser.VariableContext):
        text = ctx.getText()
        return Variable(text)

    def visitAlternative(self, ctx: CFGParser.AlternativeContext):
        return self.visit(ctx.symbol_list())

    def visitAlternative_list(self, ctx: CFGParser.Alternative_listContext):
        return remove_none([self.visit(child) for child in ctx.children])


def parse_cfg(text):
    lexer = CFGLexer(InputStream(text))
    stream = CommonTokenStream(lexer)
    parser = CFGParser(stream)
    grammar = parser.context_free_grammar()
    visitor = CFGVisitor()
    rules = visitor.visit(grammar)

    V = set([rule[0] for rule in rules])
    Sigma = set([])
    R = []
    S = rules[0][0]

    def parse_symbol(text: str) -> Union[Variable, Terminal]:
        if Variable(text) in V:
            return Variable(text)
        else:
            t = Terminal(text)
            if text != '1':
                Sigma.add(t)
            return t

    def parse_alternative(symbols: List[str]) -> Alternative:
        symbols = [parse_symbol(s) for s in symbols]
        if Terminal('1') in symbols:
            if len(symbols) != 1:
                raise RuntimeError('Symbol 1 may only appear in isolation')
            return Alternative([])
        return Alternative(symbols)

    for variable, alternatives in rules:
        for symbols in alternatives:
            rule = Rule(variable, parse_alternative(symbols))
            R.append(rule)
    return CFG(V, Sigma, R, S)
