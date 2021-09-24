#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

import copy
from typing import List

from gambatools.cfg import CFG, Variable
from gambatools.cfg_algorithms import parse_simple_cfg, cfg_add_new_start_variable_in_place, \
    cfg_remove_epsilon_rules_in_place, cfg_eliminate_unit_rules_in_place, cfg_make_rules_of_length_two_in_place, \
    cfg_eliminate_terminals_in_place, cfg_to_chomsky, cfg_words_up_to_n
from gambatools.language_generator import compare_languages
from gambatools.notebook import print_feedback


def check_cfg_has_start_variable(G: CFG, S: Variable) -> List[str]:
    if G.S != S:
        return ['Error: the start variable should be {}'.format(S)]
    return []


def check_cfg_has_no_epsilon_rules(G: CFG) -> List[str]:
    for r in G.R:
        if r.is_epsilon() and r.variable != G.S:
            return ['Error: the CFG has an epsilon rule: {}'.format(r)]
    return []


def check_cfg_has_no_unit_productions(G: CFG) -> List[str]:
    for r in G.R:
        if r.is_unit_rule():
            return ['Error: the CFG has a unit rule: {}'.format(r)]
    return []


def check_cfg_has_right_hand_sides_of_length_at_most_two(G: CFG) -> List[str]:
    for r in G.R:
        if len(r.alternative.symbols) > 2:
            return ['Error: the CFG has a rule with more than two symbols: {}'.format(r)]
    return []


def check_cfg_is_chomsky(G: CFG) -> List[str]:
    for r in G.R:
        if not r.is_chomsky():
            return ['Error: the CFG has a rule that is not in Chomsky format: {}'.format(r)]
    return []


def cfg_apply_chomsky(G: CFG, phase: int, start_variable: str) -> CFG:
    G1 = copy.deepcopy(G)
    if phase >= 1:
        cfg_add_new_start_variable_in_place(G1, start_variable)
    if phase >= 2:
        cfg_remove_epsilon_rules_in_place(G1)
    if phase >= 3:
        cfg_eliminate_unit_rules_in_place(G1)
    if phase >= 4:
        cfg_make_rules_of_length_two_in_place(G1)
    if phase >= 5:
        cfg_eliminate_terminals_in_place(G1)
    return G1


def cfg_check_chomsky(cfg: str, cfg1: str, phase: int, start_variable: str, length: int) -> None:
    try:
        feedback = []
        G = parse_simple_cfg(cfg)
        G1 = parse_simple_cfg(cfg1)
        S = Variable(start_variable)

        if phase >= 0:
            g = cfg_to_chomsky(G) if not G.is_chomsky() else G
            g1 = cfg_to_chomsky(G1) if not G1.is_chomsky() else G1
            A1 = cfg_words_up_to_n(g1, length)
            A2 = cfg_words_up_to_n(g, length)
            feedback = feedback + compare_languages(A1, A2)
        if phase >= 1:
            feedback = feedback + check_cfg_has_start_variable(G1, S)
        if phase >= 2:
            feedback = feedback + check_cfg_has_no_epsilon_rules(G1)
        if phase >= 3:
            feedback = feedback + check_cfg_has_no_unit_productions(G1)
        if phase >= 4:
            feedback = feedback + check_cfg_has_right_hand_sides_of_length_at_most_two(G1)
        if phase >= 5:
            feedback = feedback + check_cfg_is_chomsky(G1)
        print_feedback(feedback)
    except Exception as e:
        print('Error: {}'.format(e))
