#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import codecs


def read_text(filename):
    with open(filename, 'r') as f:
        return f.read()


def write_text(filename, text):
    with open(filename, 'w') as f:
        f.write(text)


def read_utf8_text(filename):
    with codecs.open(filename,'r',encoding='utf8') as f:
        return f.read()


def write_utf8_text(filename, text):
    with codecs.open(filename,'w',encoding='utf8') as f:
        f.write(text)


def remove_comments(text: str) -> str:
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and not line.startswith('%'):
            lines.append(line)
    return '\n'.join(lines)
