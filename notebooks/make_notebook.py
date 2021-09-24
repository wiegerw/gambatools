#!/usr/bin/env python3

#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
import os
import re
import json
from typing import Dict, List, Union, Tuple, Optional

from gambatools.cfg import CFG
from gambatools.cfg_algorithms import parse_simple_cfg, cfg_print_simple, cfg_cyk_matrix, cfg_print_cyk_matrix, \
    cfg_derive_word
from gambatools.dfa import DFA
from gambatools.dfa_algorithms import parse_dfa, print_dfa, dfa_union, dfa_intersection, \
    dfa_symmetric_difference, dfa_complement, dfa_reverse
from gambatools.nfa import NFA
from gambatools.nfa_algorithms import parse_nfa, nfa_to_dfa, print_nfa
from gambatools.notebook_chomsky import cfg_apply_chomsky
from gambatools.pda import PDA
from gambatools.pda_algorithms import parse_pda
from gambatools.regexp import Regexp
from gambatools.regexp_algorithms import dfa_to_regexp, print_regexp_simple
from gambatools.regexp_simple_parser import parse_simple_regexp
from gambatools.text_utility import read_utf8_text, write_utf8_text, remove_comments
from gambatools.language_generator import generate_language
from gambatools.tm import TM
from gambatools.tm_algorithms import parse_tm


default_notebook_settings: Dict[str, str] = {
    'length': '8',
    'states': '0',
}


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def parse_language_file(filename: str) -> Union[DFA, NFA, PDA, CFG, TM, Regexp]:
    text = read_utf8_text(filename)
    if filename.endswith('.dfa'):
        return parse_dfa(text)
    elif filename.endswith('.nfa'):
        return parse_nfa(text)
    elif filename.endswith('.pda'):
        return parse_pda(text)
    elif filename.endswith('.tm'):
        return parse_tm(text)
    elif filename.endswith('.cfg'):
        return parse_simple_cfg(text)
    elif filename.endswith('.regexp'):
        return parse_simple_regexp(text)


def read_paragraphs(file):
    text = read_utf8_text(file).strip()

    # TODO: make removal of comments configurable
    text = re.sub(r'^%.*?$', '', text, flags=re.MULTILINE)

    paragraphs = re.split('\n\s*\n', text)
    return paragraphs


def extension(filename):
    m = re.search(r'\.(\w+)$', filename)
    if m:
        return m.group(1)
    else:
        return ''


def remove_extension(filename):
    return re.sub(r'\.\w+$', '', filename)


def unquote(word: str) -> str:
    if len(word) >= 2 and word[0] == '"' and word[-1] == '"':
        return word[1:-1]
    return word


def apply_command(command: str, arguments: List[str]) -> str:
    if command is None:
        return arguments[0]
    elif command == 'load':
        return remove_comments(read_utf8_text(arguments[0]))
    elif command == 'generate':
        filename, length = arguments[0], arguments[1]
        length = int(length)
        words = generate_language(parse_language_file(filename), length)
        words = [word if word else 'ε' for word in words]
        return ' '.join(words)
    elif command == 'nfa2dfa':
        filename = arguments[0]
        N = parse_nfa(read_utf8_text(filename))
        D: DFA = nfa_to_dfa(N)
        return print_dfa(D)
    elif command == 'dfa2regexp':
        filename = arguments[0]
        D = parse_dfa(read_utf8_text(filename))
        R = dfa_to_regexp(D)
        return print_regexp_simple(R)
    elif command == 'dfa_union':
        inputfile1, inputfile2 = arguments
        D1 = parse_dfa(read_utf8_text(inputfile1))
        D2 = parse_dfa(read_utf8_text(inputfile2))
        D = dfa_union(D1, D2)
        return print_dfa(D)
    elif command == 'dfa_intersection':
        inputfile1, inputfile2 = arguments
        D1 = parse_dfa(read_utf8_text(inputfile1))
        D2 = parse_dfa(read_utf8_text(inputfile2))
        D = dfa_intersection(D1, D2)
        return print_dfa(D)
    elif command == 'dfa_symmetric_difference':
        inputfile1, inputfile2 = arguments
        D1 = parse_dfa(read_utf8_text(inputfile1))
        D2 = parse_dfa(read_utf8_text(inputfile2))
        D = dfa_symmetric_difference(D1, D2)
        return print_dfa(D)
    elif command == 'dfa_complement':
        inputfile = arguments[0]
        D = parse_dfa(read_utf8_text(inputfile))
        D = dfa_complement(D)
        return print_dfa(D)
    elif command == 'dfa_reverse':
        inputfile = arguments[0]
        D = parse_dfa(read_utf8_text(inputfile))
        N = dfa_reverse(D)
        return print_nfa(N)
    elif command == 'cfg_cyk_matrix':
        inputfile, word = arguments
        G = parse_language_file(inputfile)
        if not G.is_chomsky():
            raise RuntimeError('the grammar is not in Chomsky format')
        X = cfg_cyk_matrix(G, word)
        return cfg_print_cyk_matrix(X, len(word))
    elif command == 'cfg_start_symbol':
        inputfile = arguments[0]
        G = parse_language_file(inputfile)
        return G.S
    elif command in ['cfg_leftmost_derivation', 'cfg_rightmost_derivation']:
        derivation_type = command.replace('cfg_','').replace('_derivation', '')
        inputfile, word = arguments
        G = parse_language_file(inputfile)
        if G.is_chomsky():
            derivation = cfg_derive_word(G, word, derivation_type)
            derivation = ' => '.join(''.join(element) for element in derivation)
        else:
            derivation = '{} => '.format(G.S)
            print('Warning: no derivation was generated for the word "{}", because the grammar is not in Chomsky format.'.format(word))
        return derivation
    elif command in ['chomsky1', 'chomsky2', 'chomsky3', 'chomsky4', 'chomsky5']:
        filename, start_variable = arguments[0], arguments[1]
        G = parse_language_file(filename)
        phase = int(command[-1])
        return cfg_print_simple(cfg_apply_chomsky(G, phase, start_variable))
    raise RuntimeError('unknown notebook command {}'.format(command))


# Parse a tag like <<length>> or <<load(inputfile)?>>
def parse_template_tag(text: str) -> Tuple[Optional[str], List[str], bool]:
    optional = text.endswith('?')
    if optional:
        text = text[:-1]
    if '(' in text:
        m = re.fullmatch(r'(\w+)\((.*)\)', text)
        if not m:
            raise RuntimeError('Error: the tag {} is ill formed'.format(text))
        name = m.group(1)
        arguments = m.group(2).split(',')
        arguments = [arg.strip() for arg in arguments]
    else:
        name = None
        arguments = [text]
    return name, arguments, optional


def make_notebook(outputfile, notebook_settings: Dict[str, str], with_answers: bool) -> None:
    if not 'templatefile' in notebook_settings:
        raise RuntimeError('Error: a paragraph must have an entry templatefile')
    template_file = notebook_settings['templatefile']
    text = read_utf8_text(template_file)

    for m in re.finditer(r'<<(.*?)>>', text, flags=re.MULTILINE):
        source = m.group(0)
        key = m.group(1)
        command, arguments, optional = parse_template_tag(key)
        if optional and not with_answers:
            target = ''
        else:
            for arg in arguments:
                if not arg in notebook_settings:
                    raise RuntimeError('Error: the following tag was not specified: {}'.format(arg))
            arguments = [notebook_settings[arg] for arg in arguments]
            target = apply_command(command, arguments)

        text = text.replace(source, unquote(json.dumps(target)))
    write_utf8_text(outputfile, text)


def extract_template_keys(notebook_file) -> List[str]:
    result = set()
    text = read_utf8_text(notebook_file)
    for key in re.findall(r'<<.*?>>', text, flags=re.DOTALL):
        key = key[2:-2]
        command, arguments, optional = parse_template_tag(key)
        for arg in arguments:
            result.add(arg)
    return list(result)


def extract_key_value_pairs(text: str, prefix=r'\s*') -> Dict[str, str]:
    result = {}
    for m in re.finditer(prefix + r'(\w+?)\s*=(.*)$', text, flags=re.MULTILINE):
        key = m.group(1)
        value = m.group(2).strip()
        result[key] = value
    return result


def parse_paragraph(paragraph: str) -> Dict[str, str]:
    paragraph_tags = extract_key_value_pairs(paragraph)
    notebook_settings = default_notebook_settings.copy()

    # if the tag 'inputfile' exists, extract the key/value pairs from it
    if 'inputfile' in paragraph_tags:
        input_file = paragraph_tags['inputfile']
        input_tags = extract_key_value_pairs(read_utf8_text(input_file), prefix=r'%%\s*')
        notebook_settings.update(input_tags)

    # tags in the paragraph have priority over tags in the answer file
    notebook_settings.update(paragraph_tags)

    # apply @key@ substitutions
    sigma = dict()
    for key, value in notebook_settings.items():
        for m in re.finditer(r'(@\w+?@)', value):
            source = m.group(1)
            if source[1:-1] not in notebook_settings:
                raise ('Error: cannot find a replacement for @{}@'.format(source))
            target = notebook_settings[source[1:-1]]
            notebook_settings[key] = notebook_settings[key].replace(source, target)

    return notebook_settings


def generate_latex(outputfile: str, questions: List[str]):
    questions = ['\\item ' + question for question in questions]
    text = '''\\section*{{Exercise set: }}

\\begin{{enumerate}}
{}
\\end{{enumerate}}'''.format('\n\n'.join(questions))
    print('Creating {}'.format(outputfile))
    write_utf8_text(outputfile, text)


def main():
    cmdline_parser = argparse.ArgumentParser(formatter_class=SmartFormatter)
    cmdline_parser.add_argument('inputfile', metavar='FILE', type=str,
                                help='R|The input file. It should contain paragraphs like this:\n'
                                     '  key1 = value1\n'
                                     '  key2 = value2\n'
                                     '\n'
                                     'The following key/value pairs are supported:\n'
                                     '  accepted: a list of accepted words\n'
                                     '  inputfile: may contain additional entries "%%%% key = value"\n'
                                     '  language: a description of the language in LaTeX format\n'
                                     '  generate_words: the maximum length of generated words\n'
                                     '  name: the name of the output file\n'
                                     '  rejected: a list of rejected words\n'
                                     '  templatefile: the file that is used to generate the notebook"\n'
                                )
    cmdline_parser.add_argument('-w', '--working-directory', metavar='DIR', type=str, action = 'store',
                                help='the working directory. If specified, files are relative to this directory')
    cmdline_parser.add_argument('-o', '--output-directory', metavar='DIR', type=str, action = 'store', help='the directory where the generated output is stored')
    cmdline_parser.add_argument('--with-answers', help="insert the answer in the notebook", action="store_true")
    cmdline_parser.add_argument('--latex', help="generate LaTeX output containing a list of the questions", action="store_true")
    args = cmdline_parser.parse_args()

    output_directory = args.output_directory or 'output'
    if not os.path.isabs(output_directory):
        output_directory = os.path.join(os.getcwd(), output_directory)
    if not os.path.exists(output_directory):
        print('Creating output directory {}'.format(output_directory))
        os.makedirs(output_directory)

    if args.working_directory:
        os.chdir(args.working_directory)

    questions = []

    for i, paragraph in enumerate(read_paragraphs(args.inputfile)):
        try:
            notebook_settings = parse_paragraph(paragraph)
            questions.append(notebook_settings.get('question', 'question {}'.format(i)))

            # determine the output file
            name = notebook_settings.get('name', None)
            if not name:
                input_file = notebook_settings.get('inputfile', None)
                name = remove_extension(os.path.basename(input_file)) if input_file else 'exercise{}'.format(i)
            outputfile = os.path.join(output_directory, '{}.ipynb'.format(name))

            print('Creating {}'.format(outputfile))
            make_notebook(outputfile, notebook_settings, args.with_answers)
        except Exception as e:
            print('Error: {}'.format(e))

    if args.latex:
        outputfile = remove_extension(args.inputfile) + '.tex'
        generate_latex(outputfile, questions)


if __name__ == '__main__':
    main()
