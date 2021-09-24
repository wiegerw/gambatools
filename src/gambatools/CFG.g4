//  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
//  Software License, (See accompanying file LICENSE or copy at
//  https://www.gnu.org/licenses/gpl-3.0.txt)

grammar CFG;

context_free_grammar: rule_list ';'? ;

rule_list: rule_ (';' rule_)* ;

symbol: IDENTIFIER | '1' ;

variable: IDENTIFIER ;

symbol_list: symbol ('.' symbol)* ;

alternative: symbol_list ;

alternative_list: alternative ('|' alternative)* ;

rule_: variable '->' alternative_list ;

IDENTIFIER : [a-zA-Z_][a-zA-Z_0-9']* ;
WS : [ \r\n]+ -> channel(1) ;
