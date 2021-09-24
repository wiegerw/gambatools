//  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
//  Software License, (See accompanying file LICENSE or copy at
//  https://www.gnu.org/licenses/gpl-3.0.txt)

grammar regexp_simple;

// N.B. The order determines the precedence of the rules!
expression: '0'                                                     # ZeroExpression
          | '1'                                                     # OneExpression
          | IDENTIFIER                                              # SymbolExpression
          | expression '*'                                          # IterationExpression
          | expression expression                                   # ConcatExpression
          | expression '+' expression                               # SumExpression
          | '(' expression ')'                                      # ParensExpression
          ;

IDENTIFIER: [a-zA-Z] ;
WS : [ \r\n]+ -> channel(1) ;
LineComment  : '%' ~[\r\n]* -> channel(2) ;
