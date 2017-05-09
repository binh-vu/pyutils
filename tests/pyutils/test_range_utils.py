#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import eq_, ok_

from pyutils.range_utils import group_overlapped_range, Range


def test_group_overlapped_range():
    ranges = group_overlapped_range([Range(1, 3), Range(2, 3), Range(1, 4), Range(7, 8)])
    eq_(len(ranges), 2)
    ok_(ranges[0][0].same_range(Range(1, 4)))
    ok_(ranges[1][0].same_range(Range(7, 8)))

    eq_([(x.start, x.end) for x in ranges[0][1]], [(1, 3), (1, 4), (2, 3)])
    eq_([(x.start, x.end) for x in ranges[1][1]], [(7, 8)])

def test_group_overlapped_range_empty():
    ranges = group_overlapped_range([])
    eq_(len(ranges), 0)
