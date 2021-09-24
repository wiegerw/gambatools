#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import random

from IPython.core.display import HTML

from gambatools.cfg_algorithms import parse_simple_cfg, cfg_accepts_word
from gambatools.language_algorithms import parse_word_list
from gambatools.printing import print_words


def hide_code():
    this_cell = """$('div.cell.code_cell.rendered.selected')"""

    toggle_text = '.'  # text shown on toggle link
    target_cell = this_cell  # target cell to control with toggle
    js_hide_current = ''  # bit of JS to permanently hide code in current cell (only when toggling next cell)

    js_f_name = 'code_toggle_{}'.format(str(random.randint(1,2**64)))

    html = """
        <script>
            function {f_name}() {{
                {cell_selector}.find('div.input').toggle();
            }}

            {js_hide_current}
        </script>

        <a href="javascript:{f_name}()">{toggle_text}</a>
    """.format(
        f_name=js_f_name,
        cell_selector=target_cell,
        js_hide_current=js_hide_current,
        toggle_text=toggle_text
    )

    return HTML(html)


def check_cfg_accepts(cfg: str, word_list: str):
    try:
        G = parse_simple_cfg(cfg)
        words = parse_word_list(word_list)
        failures = []
        for word in words:
            if not cfg_accepts_word(G, word):
                failures.append(word)
        if failures:
            print('The following words should be accepted: {}'.format(print_words(failures)))
        else:
            print('OK')
    except RuntimeError as e:
        print('Error: {}'.format(e))


def check_cfg_rejects(cfg: str, word_list: str):
    G = parse_simple_cfg(cfg)
    words = parse_word_list(word_list)
    failures = []
    for word in words:
        if cfg_accepts_word(G, word):
            failures.append(word)
    if failures:
        print('The following words should be rejected: {}'.format(print_words(failures)))
    else:
        print('OK')


