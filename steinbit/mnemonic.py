#!/usr/bin/env python3

"""
Utilities to convert a list of names to a list of shortened
mnemonics
"""

import re
from collections import Counter
from math import log10
from typing import Pattern, List, Optional


def mnemonic(column: str, size: int, drop: Pattern) -> str:
    """
    For a given column find a reasonable mnemonic

    Parameters
    ----------
    column: str
        The string to find a mnemonic for
    size: int
        The maximum length of the mnemonic
    drop: Pattern
        A pattern to remove (e.g. vowels) from the string
    """
    extra = len(column) - size
    if extra <= 0:
        return column.upper()
    return drop.sub('', column.upper(), count=extra)[0:size]


def suffixes(count: int) -> List[str]:
    """
    Return suffixes (e.g. 1, 2...) for a number

    Parameters
    ----------
    count: int
        A count of occurences to create suffixes for
    """
    if count == 1:
        return ['']
    return [str(y).zfill(int(log10(count) + 1)) for y in range(1, count + 1)]


def mnemonics(
        columns: List[str],
        size: int = 8,
        drop: Optional[str] = None) -> List[str]:
    """
    For a set of names, contruct mnemonics

    Parameters
    ----------
    columns: List[str]
        A list of names to convert to a list of mnemonics

    size: int
        The maximum size of any mnemonic string

    drop: str
        A string containing characters that can be removed
    """
    if drop is None:
        pattern = re.compile(r'[AEIOUY \r\t\n]')
    else:
        pattern = re.compile(r'[%s]' % drop)
    shorts = [mnemonic(s, size, pattern) for s in columns]
    mapping = {
        x: [x[-(size + len(y)):] + y for y in suffixes(n)]
        for x, n in Counter(shorts).items()}
    result = []
    for short in shorts:
        result.append(mapping[short][0])
        del mapping[short][0]
    return result
