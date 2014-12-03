# -*- coding: utf-8 -*-
"""
"""

__title__ = 'ukmodulus'
__version__ = '0.0.1'
__author__ = 'Andrew Barrett'
__license__ = 'MIT'


import os
import re
from collections import namedtuple


ModulusWeight = namedtuple('ModulusWeight',
                           ['range_start',
                            'range_end',
                            'algorithm',
                            'weightings',
                            'exception_code'])

POSITION_U = 0
POSITION_V = 1
POSITION_W = 2
POSITION_X = 3
POSITION_Y = 4
POSITION_Z = 5
POSITION_A = 6
POSITION_B = 7
POSITION_C = 8
POSITION_D = 9
POSITION_E = 10
POSITION_F = 11
POSITION_G = 12
POSITION_H = 13

DBLAL = 'DBLAL'
MOD10 = 'MOD10'
MOD11 = 'MOD11'

_sc_subs = {}
_weightings = []
_mod_values = {
    DBLAL: 10,
    MOD10: 10,
    MOD11: 11,
}


def _clean_input(number, required_length=None):
    number = re.sub('[-\s]', '', number)
    if re.match('^\d+$', number) is None:
        raise ValueError
    if required_length is not None and len(number) != required_length:
        raise ValueError
    return number


def _get_weightings(sort_code):
    sort_code = int(sort_code)
    weightings = []
    for w in _weightings:
        if w.range_start > sort_code:
            break
        if w.range_start <= sort_code <= w.range_end:
            weightings.append(w)
    return weightings


def _combine_sort_and_account(sort_code, account_number, weighting):
    if weighting.exception_code == '5' and weighting.algorithm != 'DBLAL' and sort_code in _sc_subs:
        sort_code = _sc_subs[sort_code]
    elif weighting.exception_code == '8':
        sort_code = '090126'
    elif weighting.exception_code == '9':
        sort_code = '309634'
    combined = sort_code + account_number
    return combined


def _skip_check(weighting, combined):
    if weighting.exception_code == '3':
        if combined[POSITION_C] == '6' or combined[POSITION_C] == '9':
            return True
    elif weighting.exception_code == '6':
        if combined[POSITION_A] in '45678' and combined[POSITION_G] == combined[POSITION_H]:
            return True
    return False


def _get_weighting_to_use(weighting, combined):
    weightings = weighting.weightings
    if weighting.exception_code == '2':
        if combined[POSITION_A] != '0' and combined[POSITION_G] != '9':
            weightings = [0, 0, 1, 2, 5, 3, 6, 4, 8, 7, 10, 9, 3, 1]
        elif combined[POSITION_A] != '0' and combined[POSITION_G] == '9':
            weightings = [0, 0, 0, 0, 0, 0, 0, 0, 8, 7, 10, 9, 3, 1]
    elif weighting.exception_code == '7':
        if combined[POSITION_G] == '9':
            weightings = list(weightings)
            for ix in range(POSITION_B + 1):
                weightings[ix] = 0
    elif weighting.exception_code == '10':
        ab = combined[POSITION_A] + combined[POSITION_B]
        if ab in ('09', '99') and combined[POSITION_G] == '9':
            weightings = list(weightings)
            for ix in range(POSITION_B + 1):
                weightings[ix] = 0
    return weightings


def _exception_5_remainder_check(algorithm, combined, remainder):
    if algorithm == DBLAL:
        if remainder == 0 and combined[POSITION_H] == 0:
            return True
        else:
            check = 10 - remainder
            return check == combined[POSITION_H]
    else:
        if remainder == 1:
            return False
        if remainder == 0 and combined[POSITION_G] == 0:
            return True
        check = 11 - remainder
        return check == combined[POSITION_G]


def _run_check(sort_code, account_number, weighting):
    combined = _combine_sort_and_account(sort_code, account_number, weighting)
    if _skip_check(weighting, combined):
        return True
    weightings = _get_weighting_to_use(weighting, combined)
    total = 0
    for ix, ch in enumerate(combined):
        value = int(ch) * weightings[ix]
        if weighting.algorithm == DBLAL:
            total += sum(int(x) for x in str(value))
        else:
            total += value
    if weighting.exception_code == '1':
        total += 27
    mod_value = _mod_values.get(weighting.algorithm, None)
    remainder = total % mod_value
    if weighting.exception_code == '5':
        return _exception_5_remainder_check(weighting.algorithm, combined, remainder)
    if weighting.exception_code == '4':
        checkval = int(combined[POSITION_G] + combined[POSITION_H])
    else:
        checkval = 0
    return remainder == checkval


def validate_number(sort_code, account_number):
    """
    TODO Deal with non-standard account numbers as listed by section 4.2 in the VocaLink spec
    """
    sort_code = _clean_input(sort_code, required_length=6)
    account_number = _clean_input(account_number, required_length=8)
    weightings = _get_weightings(sort_code)
    check_count = len(_weightings)
    if not weightings:
        return True
    first_check = _weightings[0]
    if _run_check(sort_code, account_number, first_check):
        if check_count == 1 or first_check.exception_code in ('2', '9', '10', '11', '12', '13', '14'):
            return True
        return _run_check(sort_code, account_number, _weightings[1])
    else:
        if first_check.exception_code == '14':
            if account_number[7] not in '019':
                return False
            account_number = ('0' + account_number)[:8]
            return _run_check(sort_code, account_number, _weightings[0])
        if check_count == 1:
            return False
        return _run_check(sort_code, account_number, _weightings[1])


def _load_weightings():
    with open(os.path.join(os.path.dirname(__file__), 'valacdos.txt'), 'r') as f:
        for line in f.readlines():
            if not line:
                break
            split = line.split()
            column_count = len(split)
            if column_count not in [17, 18]:
                raise ValueError
            weighting = ModulusWeight(int(split[0]),
                                      int(split[1]),
                                      split[2],
                                      [int(x) for x in split[3:17]],
                                      split[17] if column_count == 18 else None)
            _weightings.append(weighting)


def _load_scsubs():
    with open(os.path.join(os.path.dirname(__file__), 'scsubtab.txt'), 'r') as f:
        for line in f.readlines():
            if not line:
                break
            split = line.split()
            if len(split) != 2:
                raise ValueError
            _sc_subs[split[0]] = split[1]


_load_weightings()
_load_scsubs()
