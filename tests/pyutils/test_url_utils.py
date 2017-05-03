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
