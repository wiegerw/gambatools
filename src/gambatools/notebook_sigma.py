#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from gambatools.draw_sigma import dfa_to_sigma, automaton_to_sigma
from gambatools.automaton_algorithms import parse_automaton
from gambatools.dfa_algorithms import parse_dfa

sigma_container_index = 0


def jupyter_html_settings(sigma_container):
    return {'container': sigma_container, 'style': 'height:800px; background-color:#E1E1E1'}


def show_automaton(text: str) -> str:
    global sigma_container_index
    A = parse_automaton(text)
    sigma_container = 'sigma-container{}'.format(sigma_container_index)
    sigma_container_index = sigma_container_index + 1
    return automaton_to_sigma(A, jupyter_html_settings(sigma_container))


def show_dfa(text: str) -> str:
    global sigma_container_index
    D = parse_dfa(text)
    sigma_container = 'sigma-container{}'.format(sigma_container_index)
    sigma_container_index = sigma_container_index + 1
    return dfa_to_sigma(D, jupyter_html_settings(sigma_container))
