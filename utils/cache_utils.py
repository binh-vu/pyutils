#!/usr/bin/python
# -*- coding: utf-8 -*-

import ujson

class Cache(object):
    
    def __init__(self):
        self.data = {}
    
    def exec_func(self, func, *args):
        key = ujson.dumps(args)
        if func.__name__ not in self.data:
            self.data[func.__name__] = {}
            
        if key not in self.data[func.__name__]:
            self.data[func.__name__][key] = func(*args)
        return self.data[func.__name__][key]
    
    def clear_func(self, func):
        del self.data[func.__name__]