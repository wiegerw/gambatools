# Generated from regexp.g4 by ANTLR 4.8
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\13")
        buf.write("\34\4\2\t\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\5\2\r\n\2")
        buf.write("\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\7\2\27\n\2\f\2\16\2\32")
        buf.write("\13\2\3\2\2\3\2\3\2\2\2\2 \2\f\3\2\2\2\4\5\b\2\1\2\5\r")
        buf.write("\7\3\2\2\6\r\7\4\2\2\7\r\7\n\2\2\b\t\7\b\2\2\t\n\5\2\2")
        buf.write("\2\n\13\7\t\2\2\13\r\3\2\2\2\f\4\3\2\2\2\f\6\3\2\2\2\f")
        buf.write("\7\3\2\2\2\f\b\3\2\2\2\r\30\3\2\2\2\16\17\f\5\2\2\17\20")
        buf.write("\7\6\2\2\20\27\5\2\2\6\21\22\f\4\2\2\22\23\7\7\2\2\23")
        buf.write("\27\5\2\2\5\24\25\f\6\2\2\25\27\7\5\2\2\26\16\3\2\2\2")
        buf.write("\26\21\3\2\2\2\26\24\3\2\2\2\27\32\3\2\2\2\30\26\3\2\2")
        buf.write("\2\30\31\3\2\2\2\31\3\3\2\2\2\32\30\3\2\2\2\5\f\26\30")
        return buf.getvalue()


class regexpParser ( Parser ):

    grammarFileName = "regexp.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'0'", "'1'", "'*'", "'.'", "'+'", "'('", 
                     "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "IDENTIFIER", "WS" ]

    RULE_expression = 0

    ruleNames =  [ "expression" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    IDENTIFIER=8
    WS=9

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return regexpParser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class OneExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a regexpParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOneExpression" ):
                return visitor.visitOneExpression(self)
            else:
                return visitor.visitChildren(self)


    class SymbolExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a regexpParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def IDENTIFIER(self):
            return self.getToken(regexpParser.IDENTIFIER, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSymbolExpression" ):
                return visitor.visitSymbolExpression(self)
            else:
                return visitor.visitChildren(self)


    class IterationExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a regexpParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(regexpParser.ExpressionContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIterationExpression" ):
                return visitor.visitIterationExpression(self)
            else:
                return visitor.visitChildren(self)


    class ConcatExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a regexpParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(regexpParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(regexpParser.ExpressionContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConcatExpression" ):
                return visitor.visitConcatExpression(self)
            else:
                return visitor.visitChildren(self)


    class SumExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a regexpParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(regexpParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(regexpParser.ExpressionContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSumExpression" ):
                return visitor.visitSumExpression(self)
            else:
                return visitor.visitChildren(self)


    class ZeroExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a regexpParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitZeroExpression" ):
                return visitor.visitZeroExpression(self)
            else:
                return visitor.visitChildren(self)


    class ParensExpressionContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a regexpParser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(regexpParser.ExpressionContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParensExpression" ):
                return visitor.visitParensExpression(self)
            else:
                return visitor.visitChildren(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = regexpParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 0
        self.enterRecursionRule(localctx, 0, self.RULE_expression, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [regexpParser.T__0]:
                localctx = regexpParser.ZeroExpressionContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 3
                self.match(regexpParser.T__0)
                pass
            elif token in [regexpParser.T__1]:
                localctx = regexpParser.OneExpressionContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 4
                self.match(regexpParser.T__1)
                pass
            elif token in [regexpParser.IDENTIFIER]:
                localctx = regexpParser.SymbolExpressionContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 5
                self.match(regexpParser.IDENTIFIER)
                pass
            elif token in [regexpParser.T__5]:
                localctx = regexpParser.ParensExpressionContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 6
                self.match(regexpParser.T__5)
                self.state = 7
                self.expression(0)
                self.state = 8
                self.match(regexpParser.T__6)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 22
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 20
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                    if la_ == 1:
                        localctx = regexpParser.ConcatExpressionContext(self, regexpParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 12
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 13
                        self.match(regexpParser.T__3)
                        self.state = 14
                        self.expression(4)
                        pass

                    elif la_ == 2:
                        localctx = regexpParser.SumExpressionContext(self, regexpParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 15
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 16
                        self.match(regexpParser.T__4)
                        self.state = 17
                        self.expression(3)
                        pass

                    elif la_ == 3:
                        localctx = regexpParser.IterationExpressionContext(self, regexpParser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 18
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 19
                        self.match(regexpParser.T__2)
                        pass

             
                self.state = 24
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[0] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 4)
         




