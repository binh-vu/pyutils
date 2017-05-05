#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List
from typing import TypeVar

T = TypeVar('T')


def append2list(c: List[T], v: T) -> List[T]:
    """Append element v to list c, and return list c"""
    c.append(v)
    return c
