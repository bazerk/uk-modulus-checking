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
_weightings = []
_positions = {
    'u': 0,
    'v': 1,
    'w': 2,
    'x': 3,
    'y': 4,
    'z': 5,
    'a': 6,
    'b': 7,
    'c': 8,
    'd': 9,
    'e': 10,
    'f': 11,
    'g': 12,
    'h': 13,
}
_mod_values = {
    'DBLAL': 10,
    'MOD10': 10,
    'MOD11': 11,
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


def _run_check(combined, weighting):
    mod_value = _mod_values.get(weighting.algorithm, None)
    if mod_value is None:
        raise ValueError('Unknown algorithm %s' % weighting.algorithm)
    total = 0
    for ix, ch in enumerate(combined):
        value = int(ch) * weighting.weightings[ix]
        if weighting.algorithm == 'DBLAL':
            total += sum(int(x) for x in str(value))
        else:
            total += value
    return (total % mod_value) == 0


def validate_number(sort_code, account_number):
    """
    TODO Deal with non-standard account numbers as listed by section 4.2 in the VocaLink spec
    """
    sort_code = _clean_input(sort_code, required_length=6)
    account_number = _clean_input(account_number, required_length=8)
    weightings = _get_weightings(sort_code)
    if not weightings:
        return True
    combined = sort_code + account_number
    # for weighting in weightings:
    return True


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

_load_weightings()
