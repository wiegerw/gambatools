#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Callable, Optional, Tuple, List, Union, Set
import re
import graphviz
from tabulate import tabulate

from gambatools.dfa import DFA
from gambatools.language_algorithms import parse_word_list
from gambatools.nfa import NFA
from gambatools.pda import PDA
from gambatools.tm import TM
from gambatools.cfg import CFG
from gambatools.regexp import Regexp
from gambatools.dfa_algorithms import State, Symbol, parse_dfa, dfa_accepts_word
from gambatools.automaton_algorithms import parse_automaton, state_set_regex, default_state_label_regex, \
    state_product_regex
from gambatools.automaton_io import automaton_to_dot
from gambatools.cfg_algorithms import cfg_accepts_word, parse_simple_cfg, cfg_words_up_to_n
from gambatools.dfa_algorithms import dfa_words_up_to_n, dfa_simulate_word
from gambatools.nfa_algorithms import nfa_accepts_word, nfa_simulate_word, nfa_words_up_to_n, parse_nfa
from gambatools.pda_algorithms import pda_simulate_word, pda_accepts_word, parse_pda, pda_words_up_to_n
from gambatools.tm_algorithms import tm_accepts_word, tm_simulate_word, parse_tm, tm_words_up_to_n
from gambatools.printing import print_words
from gambatools.text_utility import read_utf8_text
from gambatools.language_generator import check_equal_languages, compare_languages, generate_language
from gambatools.regexp_algorithms import regexp_words_up_to_n, regexp_accepts_word
from gambatools.regexp_simple_parser import parse_simple_regexp


def check_word_in_language(word: str, Sigma: Set[str]) -> None:
    for w in word:
        if not w in Sigma:
            raise RuntimeError('the symbol {} is not in the alphabet {{{}}}'.format(w, Sigma))


def check_automaton_syntax(text: str, parse: Callable) -> None:
    try:
        parse(text)
        print('OK')
    except Exception as e:
        print('Error: {}'.format(e))


def check_dfa_syntax(text: str):
    check_automaton_syntax(text, parse_dfa)


def check_nfa_syntax(text: str):
    check_automaton_syntax(text, parse_nfa)


def check_pda_syntax(text: str):
    check_automaton_syntax(text, parse_pda)


def check_tm_syntax(text: str):
    check_automaton_syntax(text, parse_tm)


def show_automaton(text: str, check: Optional[Callable] = None, state_regex=default_state_label_regex()) -> graphviz.Digraph:
    try:
        if check:
            check(text)
        A = parse_automaton(text, state_regex=state_regex)
        return automaton_to_dot(A)
    except Exception as e:
        print('Error: {}'.format(e))


def show(text: str) -> graphviz.Digraph:
    return show_automaton(text)


def show_product(text: str) -> graphviz.Digraph:
    return show_automaton(text, state_regex=state_product_regex())


def show_nfa2dfa(text: str) -> graphviz.Digraph:
    return show_automaton(text, state_regex=state_set_regex())


def show_dfa(text: str) -> graphviz.Digraph:
    return show_automaton(text, parse_dfa)


def show_nfa(text: str) -> graphviz.Digraph:
    return show_automaton(text, parse_nfa)


def show_pda(text: str) -> graphviz.Digraph:
    return show_automaton(text, parse_pda)


def show_tm(text: str) -> graphviz.Digraph:
    return show_automaton(text, parse_tm)


def language_parser(filename: str) -> Callable:
    if filename.endswith('.dfa'):
        return parse_dfa
    elif filename.endswith('.nfa'):
        return parse_nfa
    elif filename.endswith('.pda'):
        return parse_pda
    elif filename.endswith('.tm'):
        return parse_tm
    elif filename.endswith('.cfg'):
        return parse_simple_cfg
    elif filename.endswith('.regexp'):
        return parse_simple_regexp
    raise RuntimeError('Error: unknown extension in file {}'.format(filename))


def check_language_from_file(text: str, text_parser: Callable, answerfile: str, length: int = 5) -> None:
    try:
        A1 = text_parser(text)
        A2 = language_parser(answerfile)(read_utf8_text(answerfile))
        feedback = check_equal_languages(A1, A2, length)
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))


def check_dfa_language_from_file(text: str, filename: str, length: int = 5):
    check_language_from_file(text, parse_dfa, filename, length)


def check_nfa_language_from_file(text: str, filename: str, length: int = 5):
    check_language_from_file(text, parse_nfa, filename, length)


def check_pda_language_from_file(text: str, filename: str, length: int = 5):
    check_language_from_file(text, parse_pda, filename, length)


def check_tm_language_from_file(text: str, filename: str, length: int = 5):
    check_language_from_file(text, parse_tm, filename, length)


def check_cfg_language_from_file(text: str, filename: str, length: int = 5):
    check_language_from_file(text, parse_simple_cfg, filename, length)


def check_regexp_language_from_file(text: str, filename: str, length: int = 5):
    check_language_from_file(text, parse_simple_regexp, filename, length)


def check_max_states(A: Union[DFA, NFA, PDA, TM], max_states: int) -> List[str]:
    if 0 < max_states < len(A.Q):
        return ['Error: the maximum number of states ({}) is exceeded'.format(max_states)]
    return []


def print_feedback(feedback: List[str]) -> None:
    if feedback:
        for msg in feedback:
            print(msg)
    else:
        print('OK')


def check_language_from_words(text: str, parser: Callable, word_list: str, length: int, max_states: int = 0):
    try:
        A = parser(text)
        feedback = check_max_states(A, max_states)
        A_words = generate_language(A, length)
        words = parse_word_list(word_list)
        feedback.extend(compare_languages(A_words, words))
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))


def check_dfa_language_from_words(text: str, word_list: str, length: int, max_states: int = 0):
    check_language_from_words(text, parse_dfa, word_list, length, max_states)


def check_nfa_language_from_words(text: str, word_list: str, length: int, max_states: int = 0):
    check_language_from_words(text, parse_nfa, word_list, length, max_states)


def check_pda_language_from_words(text: str, word_list: str, length: int, max_states: int = 0):
    check_language_from_words(text, parse_pda, word_list, length, max_states)


def check_tm_language_from_words(text: str, word_list: str, length: int, max_states: int = 0):
    check_language_from_words(text, parse_tm, word_list, length, max_states)


def check_cfg_language_from_words(text: str, word_list: str, length: int):
    check_language_from_words(text, parse_simple_cfg, word_list, length)


def check_regexp_language_from_words(text: str, word_list: str, length: int):
    check_language_from_words(text, parse_simple_regexp, word_list, length)


def simulate_dfa(text: str, word: str) -> None:
    from IPython.core.display import display, HTML

    try:
        D = parse_dfa(text)
        check_word_in_language(word, D.Sigma)
        table = dfa_simulate_word(D, word)
        html = tabulate(table, headers=["State", "Word"], tablefmt='html')
        display(HTML(html))
    except Exception as e:
        print('Error: {}'.format(e))


def simulate_nfa(text: str, word: str) -> None:
    from IPython.core.display import display, HTML

    def make_row(row: Tuple[State, str]):
        q, word = row
        word = word if word else 'ε'
        return q, word

    try:
        N = parse_nfa(text)
        check_word_in_language(word, N.Sigma)
        if nfa_accepts_word(N, word):
            table = nfa_simulate_word(N, word)
            table = [make_row(row) for row in table]
            html = tabulate(table, headers=["State", "Word"], tablefmt='html')
            display(HTML(html))
        else:
            print('word {} can not be simulated, since it is not in the language'.format(word))
    except Exception as e:
        print('Error: {}'.format(e))


def simulate_pda(text: str, word: str) -> None:
    from IPython.core.display import display, HTML

    def make_row(row: Tuple[State, str, List[Symbol]], epsilon: str):
        q, word, stack = row
        stack = [t if t != epsilon else 'ε' for t in stack]
        word = word if word else 'ε'
        stack = re.sub(epsilon, 'ε', ''.join(stack))
        return q, word, stack

    try:
        P = parse_pda(text)
        check_word_in_language(word, P.Sigma)
        if pda_accepts_word(P, word):
            table = pda_simulate_word(P, word)
            table = [make_row(row, P.epsilon) for row in table]
            html = tabulate(table, headers=["State", "Word", "Stack"], tablefmt='html')
            display(HTML(html))
        else:
            print('Warning: {} can not be simulated, since it is not in the language'.format(word))
    except Exception as e:
        print('Error: {}'.format(e))


def simulate_tm(text: str, word: str) -> None:
    from IPython.core.display import display, HTML

    def make_row(row: Tuple[State, List[str], int], blank: str) -> Tuple[str, str]:
        q, tape, pos = row
        tape = tape[:]
        while pos < len(tape) - 1 and tape[-1] == blank:
            tape.pop()
        tape = [t if t != blank else '□' for t in tape]
        tape[pos] = 'UNDERLINE_LEFT{}UNDERLINE_RIGHT'.format(tape[pos])  # TODO: find a cleaner solution for this
        return str(q), ''.join(tape)

    try:
        T = parse_tm(text)
        check_word_in_language(word, T.Sigma)
        table = tm_simulate_word(T, word)
        table = [make_row(row, T.blank) for row in table]
        html = tabulate(table, headers=["State", "Tape", "Head"], tablefmt='html')
        html = html.replace('UNDERLINE_LEFT', '<u>')
        html = html.replace('UNDERLINE_RIGHT', '</u>')
        display(HTML(html))
    except Exception as e:
        print('Error: {}'.format(e))


def automaton_language(text: str, parser: Callable, generator: Callable, length: int) -> str:
    try:
        A = parser(text)
        words = generator(A, length)
        return print_words(words)
    except Exception as e:
        print('Error: {}'.format(e))


def dfa_language(text: str, length: int) -> str:
    return automaton_language(text, parse_dfa, dfa_words_up_to_n, length)


def nfa_language(text: str, length: int) -> str:
    return automaton_language(text, parse_nfa, nfa_words_up_to_n, length)


def pda_language(text: str, length: int) -> str:
    return automaton_language(text, parse_pda, pda_words_up_to_n, length)


def tm_language(text: str, length: int) -> str:
    return automaton_language(text, parse_tm, tm_words_up_to_n, length)


def cfg_language(text: str, length: int) -> str:
    return automaton_language(text, parse_simple_cfg, cfg_words_up_to_n, length)


def regexp_language(text: str, length: int) -> str:
    return automaton_language(text, parse_simple_regexp, regexp_words_up_to_n, length)


# EV, 5jun2020 added check_number_of_nfa_states
def check_number_of_nfa_states(nfa: str, count: int) -> None:
    try:
        N = parse_nfa(nfa)
        if len(N.Q) == count:
            print('OK')
    except Exception as e:
        print('Error: {}'.format(e))


def nfa_accepts(nfa: str, word: str) -> bool:
    try:
        N = parse_nfa(nfa)
        return nfa_accepts_word(N, word)
    except Exception as e:
        print('Error: {}'.format(e))


def regexp_accepts(regex: str, word: str) -> bool:
    try:
        r = parse_simple_regexp(regex)
        return regexp_accepts_word(r, word)
    except Exception as e:
        print('Error: {}'.format(e))


def check_automaton_accepts_rejects(A: Union[DFA, NFA, PDA, TM, CFG, Regexp], accepted: str, rejected: str) -> None:
    def accepts(A: Union[DFA, NFA, PDA, TM, CFG, Regexp], word: str) -> bool:
        if isinstance(A, DFA):
            return dfa_accepts_word(A, word)
        elif isinstance(A, NFA):
            return nfa_accepts_word(A, word)
        elif isinstance(A, PDA):
            return pda_accepts_word(A, word)
        elif isinstance(A, TM):
            return tm_accepts_word(A, word)
        elif isinstance(A, CFG):
            return cfg_accepts_word(A, word)
        elif isinstance(A, Regexp):
            return regexp_accepts_word(A, word)

    accepted_words = parse_word_list(accepted)
    rejected_words = parse_word_list(rejected)

    for word in accepted_words:
        if not accepts(A, word):
            word = word if word else 'ε'
            print("Error: word '{}' should be accepted".format(word))
            return

    for word in rejected_words:
        if accepts(A, word):
            word = word if word else 'ε'
            print("Error: word '{}' should not be accepted".format(word))
            return

    print('OK')


def check_cfg_accepts_rejects(cfg: str, accepted_words: str, rejected_words: str) -> None:
    try:
        G = parse_simple_cfg(cfg)
        check_automaton_accepts_rejects(G, accepted_words, rejected_words)
    except RuntimeError as e:
        print('Error: {}'.format(e))


def check_dfa_accepts_rejects(dfa: str, accepted_words: str, rejected_words: str) -> None:
    D = parse_dfa(dfa)
    check_automaton_accepts_rejects(D, accepted_words, rejected_words)


def check_dfa2regexp(dfa: str, regexp: str, length: int = 8) -> None:
    try:
        D = parse_dfa(dfa)
        R = parse_simple_regexp(regexp)
        feedback = check_equal_languages(R, D, length)
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))
