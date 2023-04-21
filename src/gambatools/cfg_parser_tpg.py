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
        START                -> context_free_grammar                                                   ;
        context_free_grammar -> rule_list SEMICOLON?                                                   ;
        rule_list            -> rule_ (SEMICOLON rule_)*                                               ;
        variable             -> IDENTIFIER                                                             ;
        symbol               -> IDENTIFIER | ONE                                                       ;
        symbol_list          -> symbol (DOT symbol)*                                                   ;
        alternative          -> symbol_list                                                            ;
        alternative_list     -> alternative (BAR alternative)*                                         ;
        rule_                -> variable ARROW alternative_list                                        ;
    '''


def parse_cfg(text):
    parser = CFGParser()
    parser(text)
    rules = []

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
    parser = CFGParser()
    parser('S -> 1')
    parser('S -> A.B')
    parser('''
       S -> A.B ;
       A -> 1 ;
       B -> a | b
    ''')
    parser('S -> α.β')
    parser("S -> A'.B'")
