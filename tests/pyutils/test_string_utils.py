#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyutils.string_utils import *
from nose.tools import *


class HyperLinkAnnotation(Annotation):
    def molding(self, string):
        return '<a>%s</a>' % string


class HeaderAnnotation(Annotation):
    def molding(self, string):
        return '<h1>%s</h1>' % string


def test_annotation_preview():
    string = 'I can eat glass without harm'
    annotation = HyperLinkAnnotation(string.find('glass'), string.find('glass') + 5)
    eq_(annotation.get_anchor(string), 'glass')
    eq_(annotation.preview(string, window_size=10), 'can eat glass without')
    eq_(annotation.preview(string, window_size=10, molding=True), 'can eat <a>glass</a> without')

def test_annotating_no_nested():
    string = '0123456789'
    annotations = [
        HyperLinkAnnotation(1, 4),
        HyperLinkAnnotation(6, 9)
    ]

    new_string = annotate_string(string, annotations, policy={})
    eq_(new_string, '0<a>123</a>45<a>678</a>9')


def test_annotating_nested():
    string = '0123456789'
    annotations = [
        HyperLinkAnnotation(1, 4),
        HyperLinkAnnotation(6, 9),
        HyperLinkAnnotation(2, 3),
    ]

    new_string = annotate_string(string, annotations, policy={})
    eq_(new_string, '0<a>1<a>2</a>3</a>45<a>678</a>9')


def test_annotating_nested_ignore():
    string = '0123456789'
    annotations = [
        HyperLinkAnnotation(1, 4),
        HyperLinkAnnotation(6, 9),
        HyperLinkAnnotation(2, 3),
    ]

    new_string = annotate_string(string, annotations, policy={
        'IGNORE_NESTED_ANNOTATION': True
    })
    eq_(new_string, '0<a>123</a>45<a>678</a>9')


@raises(PolicyViolation)
def test_annotating_nested_with_exception():
    string = '0123456789'
    annotations = [
        HyperLinkAnnotation(1, 4),
        HyperLinkAnnotation(6, 9),
        HyperLinkAnnotation(2, 3),
    ]

    annotate_string(string, annotations, policy={
        'NO_NESTED_ANNOTATION': True
    })


def test_annotating_cross_annotation():
    string = '0123456789'
    annotations = [
        HyperLinkAnnotation(1, 7),
        HyperLinkAnnotation(6, 9)
    ]

    # keep range which have longest length
    new_string = annotate_string(string, annotations, policy={
        'JUDGE_FUNCTION': lambda range_a, range_b: range_a.size() > range_b.size()
    })
    eq_(new_string, '0<a>123456</a>789')


@raises(PolicyViolation)
def test_annotating_cross_annotation_with_exception():
    string = '0123456789'
    annotations = [
        HyperLinkAnnotation(1, 7),
        HyperLinkAnnotation(6, 9)
    ]

    # keep range which have longest length
    annotate_string(string, annotations, policy={
        'IGNORE_CROSSED_ANNOTATION': False
    })


def test_annotating_merge():
    string = '0123456789'
    annotations = [
        HyperLinkAnnotation(1, 4),
        HyperLinkAnnotation(6, 9),
        HeaderAnnotation(1, 4)
    ]

    new_string = annotate_string(string, annotations, policy={})
    eq_(new_string, '0<a><h1>123</h1></a>45<a>678</a>9')

    new_string = annotate_string(string, annotations, policy={
        'MERGE_FUNCTION': lambda a, b: a if isinstance(a, HeaderAnnotation) else b
    })
    eq_(new_string, '0<h1>123</h1>45<a>678</a>9')
