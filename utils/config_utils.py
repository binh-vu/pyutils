#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import yaml
from collections import OrderedDict


class StringConf(str):

    def __new__(cls, string, workdir):
        # customize the constructor if needed
        obj = super(StringConf, cls).__new__(cls, string)
        obj.__workdir = workdir
        return obj

    def as_int(self):
        return int(self)

    def as_float(self):
        return float(self)

    def as_path(self):
        return os.path.abspath(os.path.join(self.__workdir, self))

    def ensure_dir_exists(self):
        if not os.path.exists(self.as_path()):
            os.makedirs(self.as_path())


class Configuration(object):

    def __init__(self, dict_object, workdir):
        # if __workdir__ is defined in dict_object, it overwrites the bounded workdir
        if '__workdir__' in dict_object:
            workdir = os.path.join(workdir, dict_object.pop('__workdir__'))
            
        self.__workdir = workdir
        self.__conf    = OrderedDict()
        
        for key, value in dict_object.iteritems():
            if type(value) is dict or isinstance(value, OrderedDict):
                self.__conf[key] = Configuration(value, workdir)
            elif isinstance(value, (str, unicode)):
                self.__conf[key] = StringConf(value, workdir)
            elif type(value) is list and len(value) > 0 and isinstance(value[0], (str, unicode)):
                self.__conf[key] = map(lambda x: StringConf(x, workdir), value)
            else:
                self.__conf[key] = value

            self.__dict__[key] = self.__conf[key]

    def set_conf(self, key, value):
        if type(value) is dict:
            value = Configuration(value, self.__workdir)
        elif type(value) is str:
            value = StringConf(value, self.__workdir)

        conf = self
        p_keys = key.split('.')
        for p_key in p_keys[:-1]:
            assert type(conf) is Configuration, 'Cannot assign property to primitive object'
            if p_key not in conf.__conf:
                conf.__conf[p_key] = Configuration(OrderedDict(), self.__workdir)
                conf.__dict__[p_key] = conf.__conf[p_key]

            conf = conf.__conf[p_key]

        assert type(conf) is Configuration, 'Cannot assign property to primitive object'
        conf.__conf[p_keys[-1]] = value
        conf.__dict__[p_keys[-1]] = value
        return self
    
    def __getattr__(self, name):
        return self.__conf[name]
    
    def __getitem__(self, name):
        return self.__conf[name]
    
    def __iter__(self):
        return self.__conf.iterkeys()


def load_config(fpath):
    # load yaml with OrderedDict to preserve order
    # http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
    def load_yaml_file(file_stream):
        def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
            class OrderedLoader(Loader):
                pass
            def construct_mapping(loader, node):
                loader.flatten_mapping(node)
                return object_pairs_hook(loader.construct_pairs(node))
            OrderedLoader.add_constructor(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                construct_mapping)
            return yaml.load(stream, OrderedLoader)
        return ordered_load(file_stream, yaml.SafeLoader)
    
    with open(fpath, 'rb') as f:
        return Configuration(load_yaml_file(f), workdir=os.path.dirname(fpath))
