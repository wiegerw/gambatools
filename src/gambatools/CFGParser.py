# Generated from CFG.g4 by ANTLR 4.8
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
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\t")
        buf.write("9\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\3\2\3\2\5\2\25\n\2\3\3\3\3\3\3\7\3\32\n\3")
        buf.write("\f\3\16\3\35\13\3\3\4\3\4\3\5\3\5\3\6\3\6\3\6\7\6&\n\6")
        buf.write("\f\6\16\6)\13\6\3\7\3\7\3\b\3\b\3\b\7\b\60\n\b\f\b\16")
        buf.write("\b\63\13\b\3\t\3\t\3\t\3\t\3\t\2\2\n\2\4\6\b\n\f\16\20")
        buf.write("\2\3\4\2\4\4\b\b\2\64\2\22\3\2\2\2\4\26\3\2\2\2\6\36\3")
        buf.write("\2\2\2\b \3\2\2\2\n\"\3\2\2\2\f*\3\2\2\2\16,\3\2\2\2\20")
        buf.write("\64\3\2\2\2\22\24\5\4\3\2\23\25\7\3\2\2\24\23\3\2\2\2")
        buf.write("\24\25\3\2\2\2\25\3\3\2\2\2\26\33\5\20\t\2\27\30\7\3\2")
        buf.write("\2\30\32\5\20\t\2\31\27\3\2\2\2\32\35\3\2\2\2\33\31\3")
        buf.write("\2\2\2\33\34\3\2\2\2\34\5\3\2\2\2\35\33\3\2\2\2\36\37")
        buf.write("\t\2\2\2\37\7\3\2\2\2 !\7\b\2\2!\t\3\2\2\2\"\'\5\6\4\2")
        buf.write("#$\7\5\2\2$&\5\6\4\2%#\3\2\2\2&)\3\2\2\2\'%\3\2\2\2\'")
        buf.write("(\3\2\2\2(\13\3\2\2\2)\'\3\2\2\2*+\5\n\6\2+\r\3\2\2\2")
        buf.write(",\61\5\f\7\2-.\7\6\2\2.\60\5\f\7\2/-\3\2\2\2\60\63\3\2")
        buf.write("\2\2\61/\3\2\2\2\61\62\3\2\2\2\62\17\3\2\2\2\63\61\3\2")
        buf.write("\2\2\64\65\5\b\5\2\65\66\7\7\2\2\66\67\5\16\b\2\67\21")
        buf.write("\3\2\2\2\6\24\33\'\61")
        return buf.getvalue()


class CFGParser ( Parser ):

    grammarFileName = "CFG.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "';'", "'1'", "'.'", "'|'", "'->'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "IDENTIFIER", "WS" ]

    RULE_context_free_grammar = 0
    RULE_rule_list = 1
    RULE_symbol = 2
    RULE_variable = 3
    RULE_symbol_list = 4
    RULE_alternative = 5
    RULE_alternative_list = 6
    RULE_rule_ = 7

    ruleNames =  [ "context_free_grammar", "rule_list", "symbol", "variable", 
                   "symbol_list", "alternative", "alternative_list", "rule_" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    IDENTIFIER=6
    WS=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Context_free_grammarContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def rule_list(self):
            return self.getTypedRuleContext(CFGParser.Rule_listContext,0)


        def getRuleIndex(self):
            return CFGParser.RULE_context_free_grammar

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitContext_free_grammar" ):
                return visitor.visitContext_free_grammar(self)
            else:
                return visitor.visitChildren(self)




    def context_free_grammar(self):

        localctx = CFGParser.Context_free_grammarContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_context_free_grammar)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.rule_list()
            self.state = 18
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==CFGParser.T__0:
                self.state = 17
                self.match(CFGParser.T__0)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Rule_listContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def rule_(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CFGParser.Rule_Context)
            else:
                return self.getTypedRuleContext(CFGParser.Rule_Context,i)


        def getRuleIndex(self):
            return CFGParser.RULE_rule_list

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRule_list" ):
                return visitor.visitRule_list(self)
            else:
                return visitor.visitChildren(self)




    def rule_list(self):

        localctx = CFGParser.Rule_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_rule_list)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self.rule_()
            self.state = 25
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 21
                    self.match(CFGParser.T__0)
                    self.state = 22
                    self.rule_() 
                self.state = 27
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SymbolContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(CFGParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return CFGParser.RULE_symbol

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSymbol" ):
                return visitor.visitSymbol(self)
            else:
                return visitor.visitChildren(self)




    def symbol(self):

        localctx = CFGParser.SymbolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_symbol)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            _la = self._input.LA(1)
            if not(_la==CFGParser.T__1 or _la==CFGParser.IDENTIFIER):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(CFGParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return CFGParser.RULE_variable

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariable" ):
                return visitor.visitVariable(self)
            else:
                return visitor.visitChildren(self)




    def variable(self):

        localctx = CFGParser.VariableContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_variable)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 30
            self.match(CFGParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Symbol_listContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def symbol(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CFGParser.SymbolContext)
            else:
                return self.getTypedRuleContext(CFGParser.SymbolContext,i)


        def getRuleIndex(self):
            return CFGParser.RULE_symbol_list

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSymbol_list" ):
                return visitor.visitSymbol_list(self)
            else:
                return visitor.visitChildren(self)




    def symbol_list(self):

        localctx = CFGParser.Symbol_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_symbol_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 32
            self.symbol()
            self.state = 37
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==CFGParser.T__2:
                self.state = 33
                self.match(CFGParser.T__2)
                self.state = 34
                self.symbol()
                self.state = 39
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AlternativeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def symbol_list(self):
            return self.getTypedRuleContext(CFGParser.Symbol_listContext,0)


        def getRuleIndex(self):
            return CFGParser.RULE_alternative

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAlternative" ):
                return visitor.visitAlternative(self)
            else:
                return visitor.visitChildren(self)




    def alternative(self):

        localctx = CFGParser.AlternativeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_alternative)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 40
            self.symbol_list()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Alternative_listContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def alternative(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(CFGParser.AlternativeContext)
            else:
                return self.getTypedRuleContext(CFGParser.AlternativeContext,i)


        def getRuleIndex(self):
            return CFGParser.RULE_alternative_list

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAlternative_list" ):
                return visitor.visitAlternative_list(self)
            else:
                return visitor.visitChildren(self)




    def alternative_list(self):

        localctx = CFGParser.Alternative_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_alternative_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 42
            self.alternative()
            self.state = 47
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==CFGParser.T__3:
                self.state = 43
                self.match(CFGParser.T__3)
                self.state = 44
                self.alternative()
                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Rule_Context(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variable(self):
            return self.getTypedRuleContext(CFGParser.VariableContext,0)


        def alternative_list(self):
            return self.getTypedRuleContext(CFGParser.Alternative_listContext,0)


        def getRuleIndex(self):
            return CFGParser.RULE_rule_

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitRule_" ):
                return visitor.visitRule_(self)
            else:
                return visitor.visitChildren(self)




    def rule_(self):

        localctx = CFGParser.Rule_Context(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_rule_)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.variable()
            self.state = 51
            self.match(CFGParser.T__4)
            self.state = 52
            self.alternative_list()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





