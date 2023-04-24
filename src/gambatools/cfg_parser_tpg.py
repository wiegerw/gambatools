#!/usr/bin/env python3

#  (C) Copyright Wieger Wesselink 2023. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import tpg
from gambatools.cfg import *


class CFGParser(tpg.Parser):
    '''
        separator space: '\s+' ;
        separator comments: '%.*' ;
        token ONE              '1'                                                                     ;
        token DOT              '\.'                                                                    ;
        token BAR              '\|'                                                                    ;
        token ARROW            '->'                                                                    ;
        token SEMICOLON        ';'                                                                     ;
        token IDENTIFIER       "[α-ωa-zA-Z_][α-ωa-zA-Z_0-9']*"                                         ;

        # productions
        START/rules                -> context_free_grammar/rules                                       ;
        context_free_grammar/rules -> rule_list/rules SEMICOLON?                                       ;

        rule_list/rules               ->                             $ rules = [] $
                                         rule_/r                     $ rules.append(r) $
                                         (
                                           SEMICOLON
                                           rule_/r                   $ rules.append(r) $
                                         )*                                                            ;
        variable/var                  -> IDENTIFIER/var                                                ;
        symbol/s                      -> IDENTIFIER/s  |  ONE/s                                        ;
        symbol_list/symbols           ->                             $ symbols = [] $
                                         symbol/s                    $ symbols.append(s) $
                                         (
                                         DOT
                                         symbol/s                    $ symbols.append(s) $
                                         )*                                                            ;
        alternative/symbols           -> symbol_list/symbols                                           ;
        alternative_list/alternatives ->                             $ alternatives = [] $
                                         alternative/a               $ alternatives.append(a) $
                                         (
                                         BAR
                                         alternative/a               $ alternatives.append(a) $
                                         )*                                                            ;
        rule_/r                      -> variable/var
                                        ARROW
                                        alternative_list/alternatives $ r = (var, alternatives) $      ;
    '''


def parse_cfg(text):
    parser = CFGParser()
    rules = parser(text)

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


if __name__ == "__main__":
    def f(text):
        G = parse_cfg(text)
        print('--------------------')
        print(G)

    f('S -> 1')
    f('S -> A.B')
    f('''
       S -> A.B ;
       A -> 1 ;
       B -> a | b
    ''')
    f('S -> α.β')
    f("S -> A'.B'")
