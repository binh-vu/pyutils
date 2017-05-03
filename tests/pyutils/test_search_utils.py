#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyutils import search
from nose.tools import *


def test_binary_search_empty_array():
    array = []
    eq_(search.binary_search(array, 1), len(array))


def test_binary_search_not_found():
    array = [2, 3, 4, 4, 7, 9]
    eq_(search.binary_search(array, 6), 4)
    eq_(search.binary_search(array, 10), len(array))
    eq_(search.binary_search(array, 1), 0)
    eq_(search.binary_search(array, 2.5), 1)


def test_binary_search_found():
    array = [2, 3, 4, 4, 7, 9]
    eq_(search.binary_search(array, 2), 0)
    eq_(search.binary_search(array, 4), 2)
    eq_(search.binary_search(array, 9), len(array) - 1)


def test_binary_search_key_func():
    array = list(enumerate([2, 3, 4, 4, 7, 9]))
    eq_(search.binary_search(array, 2, key=lambda x: x[1]), 0)
    eq_(search.binary_search(array, 4, key=lambda x: x[1]), 2)
    eq_(search.binary_search(array, 9, key=lambda x: x[1]), len(array) - 1)

    eq_(search.binary_search(array, 2, key=lambda x: x[0]), 2)
    eq_(search.binary_search(array, 4, key=lambda x: x[0]), 4)
    eq_(search.binary_search(array, 9, key=lambda x: x[0]), len(array))


def test_range_overlap_search_empty_array():
    array = []
    eq_(search.range_overlap_search(array, (2, 3)), [])


def test_range_overlap_search_empty_range():
    array = [(0, 3), (4, 5), (6, 7), (10, 13), (14, 18)]
    eq_(search.range_overlap_search(array, (7, 7)), [])

    array = list(enumerate([(0, 3), (4, 5), (6, 7), (10, 13), (14, 18)]))
    eq_(search.range_overlap_search(array, (10, 10), key=lambda a: a[1]), [])
    eq_(search.range_overlap_search(array, (7, 7), key=lambda a: a[1]), [])


def test_range_overlap_search_no_overlap():
    array = [(0, 3), (4, 5), (10, 13), (14, 18)]
    eq_(search.range_overlap_search(array, (7, 9)), [])
    eq_(search.range_overlap_search(array, (-3, -1)), [])
    eq_(search.range_overlap_search(array, (20, 23)), [])


def test_range_overlap_search_overlap():
    array = [(0, 3), (4, 5), (10, 13), (14, 18)]
    eq_(search.range_overlap_search(array, (0, 2)), [(0, 3)])
    eq_(search.range_overlap_search(array, (1, 4.5)), [(0, 3), (4, 5)])
    eq_(search.range_overlap_search(array, (1, 12)), [(0, 3), (4, 5), (10, 13)])
    eq_(search.range_overlap_search(array, (4.5, 19)), [(4, 5), (10, 13), (14, 18)])


def test_range_overlap_search_key_func():
    def key(x): return x[1]
    
    array = list(enumerate([(0, 3), (4, 5), (10, 13), (14, 18)]))
    eq_(search.range_overlap_search(array, (0, 2), key=key), [(0, (0, 3))])
    eq_(search.range_overlap_search(array, (1, 4.5), key=key), [(0, (0, 3)), (1, (4, 5))])
    eq_(search.range_overlap_search(array, (1, 12), key=key), [(0, (0, 3)), (1, (4, 5)), (2, (10, 13))])
    eq_(search.range_overlap_search(array, (4.5, 19), key=key), [(1, (4, 5)), (2, (10, 13)), (3, (14, 18))])

    eq_(search.range_overlap_search(array, (-3, -1), key=key), [])
    eq_(search.range_overlap_search(array, (20, 23), key=key), [])
