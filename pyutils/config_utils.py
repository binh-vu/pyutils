#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import shutil
from collections import OrderedDict
from typing import Dict, Iterable, TypeVar, Union

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

    def ensure_path_existence(self):
        path = self.as_path()
        _, ext = os.path.splitext(path)

        if ext != '':
            # this is a file
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        else:
            if not os.path.exists(path):
                os.makedirs(path)

    def backup_path(self):
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
        self.ensure_path_existence()


RawPrimitiveType = TypeVar('RawPrimitiveType', int, float, str)
PrimitiveType = TypeVar('PrimitiveType', int, float, StringConf)


class Configuration(object):

    def __init__(self, dict_object: Dict[str, Union[RawPrimitiveType, Dict]], workdir: str = '', init: bool=True) -> None:
        # if __workdir__ is defined in dict_object, it overwrites the bounded workdir
        if '__workdir__' in dict_object:
            workdir = os.path.join(workdir, dict_object['__workdir__'])

        self.__dict_object = dict_object  # Dict
        self.__workdir = workdir  # type: str
        self.__conf = OrderedDict()  # type: OrderedDict[str, Union[PrimitiveType, Configuration]]

        for key, value in dict_object.items():
            if key in {'__workdir__'}:
                continue

            if isinstance(value, (dict, OrderedDict)):
                self.__conf[key] = Configuration(value, workdir, False)
            elif isinstance(value, str):
                self.__conf[key] = StringConf(value, workdir)
            elif type(value) is list and len(value) > 0 and isinstance(value[0], str):
                self.__conf[key] = map(lambda x: StringConf(x, workdir), value)
            else:
                self.__conf[key] = value

        if init:
            self.defer_init(self, self)

    def defer_init(self, global_conf: 'Configuration', config: 'Configuration'):
        """Initialize value in config"""
        for prop in list(config.__conf.keys()):
            value = config.__conf[prop]
            if isinstance(value, StringConf):
                if value.startswith('@@'):
                    # value is a reference to other value as path
                    value = global_conf.get_conf(value[2:]).as_path()
                elif value.startswith('@'):
                    value = global_conf.get_conf(value[1:])
                config.__conf[prop] = value
            elif isinstance(value, Configuration):
                self.defer_init(global_conf, value)

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
        return iter(self.__conf.keys())

    def to_dict(self, including_workdir=False) -> Dict[str, Union[RawPrimitiveType, Dict]]:
        dict_object = {}
        if including_workdir:
            dict_object['__workdir__'] = self.__workdir

        for k, v in self.__conf.items():
            if isinstance(v, Configuration):
                v = v.to_dict()
            elif isinstance(v, StringConf):
                v = str(v)
            dict_object[k] = v
        return dict_object

    def to_raw_dict(self):
        return self.__dict_object


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

        # noinspection PyTypeChecker
        return ordered_load(file_stream, yaml.SafeLoader)

    with open(fpath, 'r') as f:
        return Configuration(load_yaml_file(f), workdir=os.path.dirname(fpath))


def write_config(config: Configuration, fpath: str) -> None:
    def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwargs):
        class OrderedDumper(Dumper):
            pass

        def _dict_representer(dumper, data):
            return dumper.represent_mapping(
                yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                data.items())

        OrderedDumper.add_representer(OrderedDict, _dict_representer)
        return yaml.dump(data, stream, OrderedDumper, **kwargs)

    with open(fpath, 'w') as f:
        ordered_dump(config.to_raw_dict(), f, default_flow_style=False, indent=4)
