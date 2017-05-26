#!/usr/bin/python
# -*- coding: utf-8 -*-

from nose.tools import *

from pyutils.url_utils import parse


def test_parse():
    url = 'http://vnexpress.net/article?q=haha&limit'
    url_param = parse(url)
    eq_(url_param.scheme, 'http')
    eq_(url_param.netloc, 'vnexpress.net')
    eq_(url_param.path, '/article')
    eq_(url_param.params, '')
    eq_(url_param.query, {'q': ['haha'], 'limit': ['']})
    eq_(url_param.get_query_param('q'), 'haha')
    eq_(url_param.get_query_param('limit'), '')


def test_parse_with_fragment():
    url = 'http://vnexpress.net/article?q=haha&limit#q=software+engineer&start=50'
    url_param = parse(url)
    eq_(url_param.fragment, {'q': ['software engineer'], 'start': ['50']})
    eq_(url_param.get_fragment_param('q'), 'software engineer')
    eq_(url_param.get_fragment_param('start'), '50')


def test_parse_with_fragment_str():
    url = 'http://vnexpress.net/article?q=haha&limit#headline'
    url_param = parse(url)
    eq_(url_param.fragment, {'headline': ['']})
