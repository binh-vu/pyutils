#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import OrderedDict
from typing import Dict, Union
from typing import List
from urllib.parse import urlencode
from urllib.parse import urlparse, parse_qs, urlunparse


class URLParam(object):
    def __init__(self, scheme: str, netloc: str, path: str, params: str, query: Dict[str, List[str]], fragment: str):
        self.scheme: str = scheme
        self.netloc: str = netloc
        self.path: str = path
        self.params: str = params
        self.query: Dict[str, List[str]] = query
        self.fragment: str = fragment

    def get_query_param(self, name: str) -> Union[str, List[str]]:
        value = self.query[name]
        if len(value) == 1:
            return value[0]
        return value

    def add_query_param(self, name: str, value: str):
        self.query[name] = value

    def keep_query_params(self, query_params: List[str]):
        self.query = OrderedDict([
            (x, self.query[x])
            for x in query_params
            if x in self.query
        ])

    def build_url(self) -> str:
        return urlunparse((
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            urlencode(self.query, doseq=True),
            self.fragment
        ))


def parse(url: str) -> URLParam:
    result = urlparse(url)
    url_param = URLParam(*result)
    url_param.query = parse_qs(url_param.query, keep_blank_values=True)

    return url_param
