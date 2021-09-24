# Generated from CFG.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\t")
        buf.write("*\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\3\2\3\2\3\3\3\3\3\4\3\4\3\5\3\5\3\6\3\6\3\6\3")
        buf.write("\7\3\7\7\7\37\n\7\f\7\16\7\"\13\7\3\b\6\b%\n\b\r\b\16")
        buf.write("\b&\3\b\3\b\2\2\t\3\3\5\4\7\5\t\6\13\7\r\b\17\t\3\2\5")
        buf.write("\5\2C\\aac|\7\2))\62;C\\aac|\5\2\f\f\17\17\"\"\2+\2\3")
        buf.write("\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2")
        buf.write("\2\2\2\r\3\2\2\2\2\17\3\2\2\2\3\21\3\2\2\2\5\23\3\2\2")
        buf.write("\2\7\25\3\2\2\2\t\27\3\2\2\2\13\31\3\2\2\2\r\34\3\2\2")
        buf.write("\2\17$\3\2\2\2\21\22\7=\2\2\22\4\3\2\2\2\23\24\7\63\2")
        buf.write("\2\24\6\3\2\2\2\25\26\7\60\2\2\26\b\3\2\2\2\27\30\7~\2")
        buf.write("\2\30\n\3\2\2\2\31\32\7/\2\2\32\33\7@\2\2\33\f\3\2\2\2")
        buf.write("\34 \t\2\2\2\35\37\t\3\2\2\36\35\3\2\2\2\37\"\3\2\2\2")
        buf.write(" \36\3\2\2\2 !\3\2\2\2!\16\3\2\2\2\" \3\2\2\2#%\t\4\2")
        buf.write("\2$#\3\2\2\2%&\3\2\2\2&$\3\2\2\2&\'\3\2\2\2\'(\3\2\2\2")
        buf.write("()\b\b\2\2)\20\3\2\2\2\5\2 &\3\2\3\2")
        return buf.getvalue()


class CFGLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    IDENTIFIER = 6
    WS = 7

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "';'", "'1'", "'.'", "'|'", "'->'" ]

    symbolicNames = [ "<INVALID>",
            "IDENTIFIER", "WS" ]

    ruleNames = [ "T__0", "T__1", "T__2", "T__3", "T__4", "IDENTIFIER", 
                  "WS" ]

    grammarFileName = "CFG.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


