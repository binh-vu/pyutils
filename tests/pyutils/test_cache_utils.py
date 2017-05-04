#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time

from nose.tools import *

from pyutils.cache_utils import Cache, FileCache, FileCacheDelegator


class Counter(object):
    def __init__(self):
        self.count = 0

    def increase(self, message):
        self.count += 1
        return self.count, message


def test_memory_cache():
    cache = Cache()

    counter = Counter()
    count, mess = cache.exec_func(counter.increase, 'messA')
    eq_(counter.count, 1, 'Increase func is called')
    eq_(count, 1, 'Cache return correct result')
    eq_(mess, 'messA')
    count, mess = cache.exec_func(counter.increase, 'messA')
    eq_(count, 1, 'Return previous cached result')
    eq_(counter.count, 1, 'Increase func is not called')
    eq_(mess, 'messA')
    count, mess = cache.exec_func(counter.increase, 'messB')
    eq_(count, 2, 'Increate function is called because diff args')
    eq_(mess, 'messB')


def test_file_cache():
    timeid = time.time()
    cache_file = f'/tmp/file_cache_{timeid}.txt'
    ok_(not os.path.exists(cache_file))

    counter = Counter()
    # no-previous cached data
    cache = FileCache(cache_file)
    cache.load_data()
    with cache:
        count, mess = cache.exec_func(counter.increase, 'messA')
        eq_(counter.count, 1, 'Increase func is called')
        eq_(count, 1, 'Cache return correct result')
        count, mess = cache.exec_func(counter.increase, 'messA')
        eq_(count, 1, 'Return previous cached result')
        eq_(counter.count, 1, 'Increase func is not called')
        count, mess = cache.exec_func(counter.increase, 'messB')
        eq_(count, 2, 'Increate function is called because diff args')
        eq_(mess, 'messB')

    # had cached data
    counter = Counter()
    cache = FileCache(cache_file)
    cache.load_data()
    with cache:
        count, mess = cache.exec_func(counter.increase, 'messA')
        eq_(count, 1, 'Return previous cached result')
        eq_(counter.count, 0, 'Increase func is not called')
        count, mess = cache.exec_func(counter.increase, 'messB')
        eq_(count, 2, 'Return previous cached result')
        eq_(counter.count, 0, 'Increase func is not called')

    # when not load data, the function has not been cached
    counter = Counter()
    cache = FileCache(cache_file)
    with cache:
        count, mess = cache.exec_func(counter.increase, 'messA')
        eq_(count, 1, 'Cache return correct result')
        eq_(counter.count, 1, 'Increase func is called')

    # invalidate the old data
    counter = Counter()
    cache = FileCache(cache_file)
    cache.load_data()
    with cache:
        count, mess = cache.exec_func(counter.increase, 'messA')
        eq_(count, 1, 'Return previous cached result')
        eq_(counter.count, 0, 'Increase func is not called')

        cache.invalidate()
        count, mess = cache.exec_func(counter.increase, 'messA')
        eq_(counter.count, 1, 'Increase func is called')
        eq_(count, 1, 'Cache return correct result')


@raises(AssertionError)
def test_file_cache_must_context():
    timeid = time.time()
    cache_file = f'/tmp/file_cache_{timeid}.txt'
    ok_(not os.path.exists(cache_file))

    counter = Counter()
    # no-previous cached data
    cache = FileCache(cache_file)
    cache.load_data()
    cache.exec_func(counter.increase)


def test_cache_delegator():
    def create_counter():
        return Counter()

    timeid = time.time()
    cache_file = f'/tmp/file_cache_{timeid}.txt'
    ok_(not os.path.exists(cache_file))

    # no-previous cached data
    cache_delegator = FileCacheDelegator(cache_file, create_counter)
    cache_delegator.load_data()
    with cache_delegator:
        count, mess = cache_delegator.increase('messA')
        eq_(count, 1, 'Increase function is called')
        count, mess = cache_delegator.increase('messA')
        eq_(count, 1, 'Result have been cached')
        count, mess = cache_delegator.increase('messB')
        eq_(count, 2, 'Increate function is called because diff args')


@raises(AssertionError)
def test_cache_delegator_must_context():
    def create_counter():
        return Counter()

    timeid = time.time()
    cache_file = f'/tmp/file_cache_{timeid}.txt'
    ok_(not os.path.exists(cache_file))

    counter = Counter()
    # no-previous cached data
    cache = FileCacheDelegator(cache_file, create_counter)
    cache.load_data()
    cache.exec_func(counter.increase, 'messA')
