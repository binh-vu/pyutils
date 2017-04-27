#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib

def md5(string):
    if type(string) is unicode:
        string = string.encode('utf-8')
    algo = hashlib.md5()
    algo.update(string)

    return algo.hexdigest()