#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os
import shutil
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

    def ensure_dir_existence(self):
        if not os.path.exists(self.as_path()):
            os.makedirs(self.as_path())

    def backup_dir(self):
        path = self.as_path()
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)

        if os.path.exists(path):
            # find the most recent back up
            backup_reg = re.compile('^-\d+$')
            backup_versions = [
                int(fname.replace(basename + '-', ''))
                for fname in os.listdir(dirname)
                if fname.startswith(basename) and backup_reg.match(fname.replace(basename, '')) is not None
            ]
            if len(backup_versions) == 0:
                most_recent_version = 0
            else:
                most_recent_version = max(backup_versions)

            # do the backup
            shutil.move(path, os.path.join(dirname, basename + '-' + str(most_recent_version + 1)))

        # create new folder to work with
        self.ensure_dir_existence()


class Configuration(object):

    def __init__(self, dict_object, workdir=''):
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

    def get_conf(self, key):
        """
            Get configuration provided by the dot string
            :param key:
            :return:
        """
        conf = self
        props = key.split('.')
        for prop in props[:-1]:
            conf = conf.__conf[prop]
        return conf.__conf[props[-1]]

    def __getattr__(self, name):
        return self.__conf[name]
    
    def __getitem__(self, name):
        return self.__conf[name]
    
    def __iter__(self):
        return self.__conf.iterkeys()

    def to_dict(self):
        dict_object = {
            '__workdir__': self.__workdir
        }
        for k, v in self.__conf.iteritems():
            if isinstance(v, Configuration):
                v = v.to_dict()
            dict_object[k] = v
        return dict_object


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


def write_config(config, fpath):
    with open(fpath, 'wb') as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False)
