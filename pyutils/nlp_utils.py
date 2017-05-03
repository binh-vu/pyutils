#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from html.parser import HTMLParser
from pycorenlp import StanfordCoreNLP

nlp = None


def get_nlp():
    global nlp
    if nlp is None:
        nlp = StanfordCoreNLP('http://localhost:9000')
    return nlp


def tokenize(text, return_position=False):
    output = get_nlp().annotate(text.encode('utf-8'),
                                properties={'annotators': 'tokenize,ssplit', 'outputFormat': 'json'})
    tokens = []
    position = []

    for sentence in output['sentences']:
        for token in sentence['tokens']:
            offset = token['characterOffsetBegin']
            for i, x in enumerate(token['originalText'].split('/')):
                if x == '':
                    continue

                position.append((offset, offset + len(x)))
                tokens.append(x)
                offset = offset + len(x) + 1

    if return_position:
        return tokens, position
    return tokens


class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    def error(self, message):
        raise Exception(message)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def find_all(substring, string):
    """
        Find all occurrences of substring in string
    """
    tmp = string
    offset = 0
    occurrences = []
    while tmp.find(substring) != -1:
        occurrences.append(tmp.find(substring) + offset)
        offset += tmp.find(substring) + len(substring)
        tmp = tmp[tmp.find(substring) + len(substring):]

    return occurrences


def match_sequence(seq_a, seq_b, start_index, case_insensitive=True):
    """
        Test if seqA is starts with seqB
    """
    if len(seq_a) - start_index < len(seq_b):
        return False

    if case_insensitive:
        for i in range(len(seq_b)):
            if seq_a[i + start_index].lower() != seq_b[i].lower():
                return False
    else:
        for i in range(len(seq_b)):
            if seq_a[i + start_index] != seq_b[i]:
                return False

    return True


def get_match_positions(query_tokens, tokens):
    matches = []

    for i in range(len(tokens)):
        if match_sequence(tokens, query_tokens, i):
            matches.append(i)

    return matches


def get_hashtag(text):
    tags = re.findall('(#[a-zA-Z_]+)', text)
    return set(tags)
