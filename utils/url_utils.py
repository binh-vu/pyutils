#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from urlparse import urlparse, parse_qs, urlunparse
from urllib import urlencode

class URLParam(object):

    def __init__(self, scheme, netloc, path, params, query, fragment):
        self.scheme = scheme
        self.netloc = netloc
        self.path = path
        self.params = params
        self.query = query
        self.fragment = fragment

    def get_query_param(self, name):
        value = self.query[name]
        if len(value) == 1:
            return value[0]
        return value

    def add_query_param(self, name, value):
        self.query[name] = value
        return self

    def keep_query_params(self, query_params):
        """
        :param query_params: list<string>
        :return:
        """
        self.query = OrderedDict([
            (x, self.query[x])
            for x in query_params
            if x in self.query
        ])
        return self

    def build_url(self):
        return urlunparse((
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            urlencode(self.query, doseq=True),
            self.fragment
        ))

def parse(url):
    result = urlparse(url)
    url_param = URLParam(*result)
    url_param.query = parse_qs(url_param.query, keep_blank_values=True)

    return url_param