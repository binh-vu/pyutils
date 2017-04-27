#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, spacy
from HTMLParser import HTMLParser

nlp = None
def get_nlp():
    global nlp
    if nlp is None:
        """
            spaCy actually have a terrible document for custom tokenizer and it doesn't work.
            Hack directly to the internal API to make it work
        """
        # Defaults = spacy.load('en').__class__.Defaults
        # if Defaults.infixes[-1] != '/':
        #     infixes = list(Defaults.infixes)
        #     infixes.append('/')
        #     infixes = tuple(infixes)
        #     Defaults.infixes = infixes
        # if Defaults.suffixes[-1] != '/':
        #     suffixes = list(Defaults.suffixes)
        #     suffixes.append('/')
        #     suffixes = tuple(suffixes)
        #     Defaults.suffixes = suffixes
        # if Defaults.prefixes[-1] != '/':
        #     prefixes = list(Defaults.prefixes)
        #     prefixes.append('/')
        #     prefixes = tuple(prefixes)
        #     Defaults.prefixes = prefixes

        nlp = spacy.load('en')
        
    return nlp

def tokenize(text, return_position=False):
    nlp       = get_nlp()
    tokens    = nlp(text.decode('utf-8') if type(text) is str else text)
    positions = [(w.idx, w.idx + len(w.text)) for w in tokens]
    tokens    = [w.text for w in tokens]

    if return_position:
        return tokens, positions
    return tokens

class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

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

def match_sequence(seqA, seqB, start_index, case_insensitive=True):
    """
        Test if seqA is starts with seqB
    """
    if len(seqA) - start_index < len(seqB):
        return False

    if case_insensitive:
        for i in xrange(len(seqB)):
            if seqA[i + start_index].lower() != seqB[i].lower():
                return False
    else:
        for i in xrange(len(seqB)):
            if seqA[i + start_index] != seqB[i]:
                return False

    return True

def get_match_positions(query_tokens, tokens):
    matches = []

    for i in xrange(len(tokens)):
        if match_sequence(tokens, query_tokens, i):
            matches.append(i)

    return matches

def get_hashtag(text):
    tags = re.findall('(#[a-zA-Z_]+)', text)
    return set(tags)