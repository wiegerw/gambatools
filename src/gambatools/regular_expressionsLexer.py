# Generated from regexp.g4 by ANTLR 4.8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys



def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\17")
        buf.write("[\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\3\2\3\2\3\3\3\3\3\4\3\5\3\6\3\6\3\7\3\7\3\b\3\b")
        buf.write("\3\t\3\t\3\n\3\n\3\13\3\13\3\13\3\13\3\13\3\13\3\13\3")
        buf.write("\13\3\13\3\13\3\13\3\13\3\13\3\13\3\f\6\f=\n\f\r\f\16")
        buf.write("\f>\3\f\3\f\3\r\3\r\3\r\3\r\7\rG\n\r\f\r\16\rJ\13\r\3")
        buf.write("\r\3\r\3\r\3\r\3\r\3\16\3\16\3\16\3\16\7\16U\n\16\f\16")
        buf.write("\16\16X\13\16\3\16\3\16\3H\2\17\3\3\5\4\7\5\t\6\13\7\r")
        buf.write("\b\17\t\21\n\23\13\25\f\27\r\31\16\33\17\3\2\4\5\2\13")
        buf.write("\f\16\17\"\"\4\2\f\f\17\17\2]\2\3\3\2\2\2\2\5\3\2\2\2")
        buf.write("\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3\2\2\2\2\r\3\2\2\2\2\17")
        buf.write("\3\2\2\2\2\21\3\2\2\2\2\23\3\2\2\2\2\25\3\2\2\2\2\27\3")
        buf.write("\2\2\2\2\31\3\2\2\2\2\33\3\2\2\2\3\35\3\2\2\2\5\37\3\2")
        buf.write("\2\2\7!\3\2\2\2\t\"\3\2\2\2\13#\3\2\2\2\r%\3\2\2\2\17")
        buf.write("\'\3\2\2\2\21)\3\2\2\2\23+\3\2\2\2\25-\3\2\2\2\27<\3\2")
        buf.write("\2\2\31B\3\2\2\2\33P\3\2\2\2\35\36\7*\2\2\36\4\3\2\2\2")
        buf.write("\37 \7+\2\2 \6\3\2\2\2!\b\3\2\2\2\"\n\3\2\2\2#$\7\u00b9")
        buf.write("\2\2$\f\3\2\2\2%&\7-\2\2&\16\3\2\2\2\'(\7,\2\2(\20\3\2")
        buf.write("\2\2)*\7\62\2\2*\22\3\2\2\2+,\7\63\2\2,\24\3\2\2\2-.\7")
        buf.write("]\2\2./\7c\2\2/\60\7/\2\2\60\61\7|\2\2\61\62\7C\2\2\62")
        buf.write("\63\7/\2\2\63\64\7\\\2\2\64\65\7\62\2\2\65\66\7/\2\2\66")
        buf.write("\67\7;\2\2\678\7a\2\289\7_\2\29:\7-\2\2:\26\3\2\2\2;=")
        buf.write("\t\2\2\2<;\3\2\2\2=>\3\2\2\2><\3\2\2\2>?\3\2\2\2?@\3\2")
        buf.write("\2\2@A\b\f\2\2A\30\3\2\2\2BC\7*\2\2CD\7,\2\2DH\3\2\2\2")
        buf.write("EG\13\2\2\2FE\3\2\2\2GJ\3\2\2\2HI\3\2\2\2HF\3\2\2\2IK")
        buf.write("\3\2\2\2JH\3\2\2\2KL\7,\2\2LM\7+\2\2MN\3\2\2\2NO\b\r\3")
        buf.write("\2O\32\3\2\2\2PQ\7\61\2\2QR\7\61\2\2RV\3\2\2\2SU\n\3\2")
        buf.write("\2TS\3\2\2\2UX\3\2\2\2VT\3\2\2\2VW\3\2\2\2WY\3\2\2\2X")
        buf.write("V\3\2\2\2YZ\b\16\3\2Z\34\3\2\2\2\6\2>HV\4\2\3\2\2\4\2")
        return buf.getvalue()


class regular_expressionsLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    LPAREN = 3
    RPAREN = 4
    CONCAT = 5
    PLUS = 6
    STAR = 7
    ZERO = 8
    ONE = 9
    IDENTIFIER = 10
    WS = 11
    BlockComment = 12
    LineComment = 13

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'('", "')'", "'('", "')'", "'\u00B7'", "'+'", "'*'", "'0'", 
            "'1'", "'[a-zA-Z0-9_]+'" ]

    symbolicNames = [ "<INVALID>",
            "LPAREN", "RPAREN", "CONCAT", "PLUS", "STAR", "ZERO", "ONE", 
            "IDENTIFIER", "WS", "BlockComment", "LineComment" ]

    ruleNames = [ "T__0", "T__1", "LPAREN", "RPAREN", "CONCAT", "PLUS", 
                  "STAR", "ZERO", "ONE", "IDENTIFIER", "WS", "BlockComment", 
                  "LineComment" ]

    grammarFileName = "regexp.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


