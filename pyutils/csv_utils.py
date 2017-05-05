#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Contains pyutils for csv
"""
import csv
from io import StringIO


def dump_csv(array, delimiter=','):
    f = StringIO()
    writer = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(array)

    return f.getvalue()[:-2]
