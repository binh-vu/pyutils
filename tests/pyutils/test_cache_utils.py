#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from typing import Dict, Tuple, List, Union, Optional

import time

from pyutils.cache_utils import Cache, FileCache, FileCacheDelegator
from nose.tools import *


class Counter(object):

    def __init__(self):
        self.count = 0

    def increase(self):
        self.count += 1
        return self.count


def test_memory_cache():
    cache = Cache()

    counter = Counter()
    result = cache.exec_func(counter.increase)
    ok_(counter.count == 1, 'Increase func is called')
    ok_(result == 1, 'Cache return correct result')
    result = cache.exec_func(counter.increase)
    ok_(result == 1, 'Return previous cached result')
    ok_(counter.count == 1, 'Increase func is not called')


def test_file_cache():
    timeid = time.time()
    cache_file = f'/tmp/file_cache_{timeid}.txt'
    ok_(not os.path.exists(cache_file))

    counter = Counter()
    # no-previous cached data
    cache = FileCache(cache_file)
    try:
        cache.load_data()
        cache.open()
        result = cache.exec_func(counter.increase)
        ok_(counter.count == 1, 'Increase func is called')
        ok_(result == 1, 'Cache return correct result')
        result = cache.exec_func(counter.increase)
        ok_(result == 1, 'Return previous cached result')
        ok_(counter.count == 1, 'Increase func is not called')
    finally:
        cache.close()

    # had cached data
    counter = Counter()
    cache = FileCache(cache_file)
    try:
        cache.load_data()
        cache.open()
        result = cache.exec_func(counter.increase)
        ok_(result == 1, 'Return previous cached result')
        ok_(counter.count == 0, 'Increase func is not called')
    finally:
        cache.close()

    # invalidate the old data
    counter = Counter()
    cache = FileCache(cache_file)
    try:
        cache.load_data()
        cache.open()
        result = cache.exec_func(counter.increase)
        ok_(result == 1, 'Return previous cached result')
        ok_(counter.count == 0, 'Increase func is not called')

        cache.invalidate()
        result = cache.exec_func(counter.increase)
        ok_(counter.count == 1, 'Increase func is called')
        ok_(result == 1, 'Cache return correct result')
    finally:
        cache.close()


def test_cache_delegator():
    def create_counter():
        return Counter()

    timeid = time.time()
    cache_file = f'/tmp/file_cache_{timeid}.txt'
    ok_(not os.path.exists(cache_file))

    # no-previous cached data
    cache_delegator = FileCacheDelegator(cache_file, create_counter)
    try:
        cache_delegator.load_data()
        cache_delegator.open()
        result = cache_delegator.increase()
        ok_(result == 1, 'Increase function is called')
        result = cache_delegator.increase()
        ok_(result == 1, 'Result have been cached')
    finally:
        cache_delegator.close()
