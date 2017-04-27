#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
	Contains utils for csv
"""
import StringIO, csv

def dump_csv(array, delimiter=','):
    f = StringIO.StringIO()
    writer = csv.writer(f, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    writer.writerow([unicode(s).encode('utf-8') for s in array])

    return f.getvalue()[:-2]