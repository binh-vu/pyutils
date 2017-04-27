#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
	Define helper for Jupyter Notebook
"""
import json2html
from IPython.display import display, HTML

def print_dict(object):
    display(HTML(json2html.json2html.convert(json=object)))

def percentage(a, b):
    return '%.2f%% (%s/%s)' % (a * 100.0 / b, a, b)
