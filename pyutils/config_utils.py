#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import shutil
from collections import OrderedDict
from typing import Dict, Any, Iterable, TypeVar, Union

import yaml


class StringConf(str):
    def __new__(cls, string: str, workdir: str) -> 'StringConf':
        # customize the constructor if needed
        obj = super(StringConf, cls).__new__(cls, string)
        obj.__workdir = workdir
        return obj

    def as_int(self) -> int:
        return int(self)

    def as_float(self) -> float:
        return float(self)

    def as_path(self) -> str:
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


RawPrimitiveType = TypeVar('RawPrimitiveType', int, float, str)
PrimitiveType = TypeVar('PrimitiveType', int, float, StringConf)


class Configuration(object):

    def __init__(self, dict_object: Dict[str, Union[RawPrimitiveType, Dict]], workdir: str = '') -> None:

        # if __workdir__ is defined in dict_object, it overwrites the bounded workdir
        if '__workdir__' in dict_object:
            workdir = os.path.join(workdir, dict_object.pop('__workdir__'))

        # type: str
        self.__workdir = workdir
        # type: OrderedDict[str, Union[PrimitiveType, Configuration]]
        self.__conf = OrderedDict()

        for key, value in dict_object.items():
            if type(value) is dict or isinstance(value, OrderedDict):
                self.__conf[key] = Configuration(value, workdir)
            elif isinstance(value, str):
                self.__conf[key] = StringConf(value, workdir)
            elif type(value) is list and len(value) > 0 and isinstance(value[0], str):
                self.__conf[key] = map(lambda x: StringConf(x, workdir), value)
            else:
                self.__conf[key] = value

    def set_conf(self, key: str, value: RawPrimitiveType) -> 'Configuration':
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

            conf = conf.__conf[p_key]

        assert type(conf) is Configuration, 'Cannot assign property to primitive object'
        conf.__conf[p_keys[-1]] = value
        return self

    def get_conf(self, key: str) -> Union[PrimitiveType, 'Configuration']:
        """Get configuration provided by the dot string"""
        conf = self
        props = key.split('.')
        for prop in props[:-1]:
            conf = conf.__conf[prop]
        return conf.__conf[props[-1]]

    def __getattr__(self, name: str) -> Union[PrimitiveType, 'Configuration']:
        return self.__conf[name]

    def __getitem__(self, name: str) -> Union[PrimitiveType, 'Configuration']:
        return self.__conf[name]

    def __iter__(self) -> Iterable[str]:
        return self.__conf.keys()

    def to_dict(self) -> Dict[str, Union[RawPrimitiveType, Dict]]:
        dict_object = {
            '__workdir__': self.__workdir
        }
        for k, v in self.__conf.items():
            if isinstance(v, Configuration):
                v = v.to_dict()
            dict_object[k] = v
        return dict_object


def load_config(fpath: str) -> Configuration:
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

    with open(fpath, 'r') as f:
        return Configuration(load_yaml_file(f), workdir=os.path.dirname(fpath))


def write_config(config: Configuration, fpath: str) -> None:
    with open(fpath, 'w') as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False)
