#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Dict, Any, Callable
import ujson, os

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


class FileCache(object):

    def __init__(self, fpath):
        # type: (str) -> None
        self.fpath = fpath
        self.data = {}  # type: Dict[str, any]
        self.fcursor = None  # type: file

    def load_data(self):
        # Load data when the file's existed
        if os.path.exists(self.fpath):
            with open(self.fpath, 'rb') as f:
                for l in f:
                    k, v = ujson.loads(l)
                    self.data[k] = v

    def open(self):
        self.fcursor = open(self.fpath, mode='ab')

    def close(self):
        self.fcursor.close()

    def invalidate(self):
        if self.fcursor is not None:
            self.close()
        self.fcursor = open(self.fpath, mode='wb')

    def exec_func(self, func, *args):
        # type: (Callable[[*Any], Any], *Any) -> Any
        key = '%s:%s' % (func.__name__, ujson.dumps(args))
        if key not in self.data:
            self.data[key] = func(*args)
            self.write_change(key)

        return self.data[key]

    def write_change(self, key):
        # type: (str) -> None
        self.fcursor.write(ujson.dumps((key, self.data[key])))


class FileCacheDelegator(object):

    def __init__(self, fpath, object_constructor):
        self.file_cache = FileCache(fpath)
        self.object_constructor = object_constructor  # type: Callable[[], object]
        self.object = None  # type: object
        self.delegator = {}  # type: Dict[str, Callable[[*Any], Any]]

    def load_data(self):
        self.file_cache.load_data()

    def open(self):
        self.file_cache.open()

    def close(self):
        self.file_cache.close()

    def invalidate(self):
        self.file_cache.invalidate()

    def get_delegate_func(self, func_name):
        def delegate(*args):
            if self.object is None:
                self.object = self.object_constructor()
            return self.object.__dict__[func_name](*args)
        return delegate

    def get_exec_func(self, func):
        def exec_func(*args):
            return self.file_cache.exec_func(func, *args)
        return exec_func

    def __getattr__(self, item):
        # type: (str) -> Any
        """
        Alias of the cached function
        """
        if item not in self.delegator:
            self.delegator[item] = [
                self.get_delegate_func(item),
                self.get_exec_func(item)
            ]

        exec_func = self.delegator[item][1]
        return exec_func
