#!/usr/bin/python
# -*- coding: utf-8 -*-

import copy, simplejson as json, warnings
from datetime import datetime
from collections import OrderedDict
from bson.objectid import ObjectId

def format_dt(dt):
    if dt.tzinfo == None:
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f') + '+0000'

    return dt.strftime('%Y-%m-%d %H:%M:%S.%f%z')

class DynamicJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return { '_type': 'DateTime', 'value': format_dt(obj) }

        if isinstance(obj, ObjectId):
            return str(obj)

        for clazz in self.classes:
            if isinstance(obj, clazz):
                data = obj.__dict__
                data['_type'] = clazz.__name__

                return data

        return json.JSONEncoder.default(self, obj)

def get_object_hook(classes):
    """
        Get object hook function that can convert dict back to classes

        @param classes list<PYTHON_CLASS>
    """

    class_names = { clazz.__name__: clazz for clazz in classes }

    def object_hook(data):
        if '_type' in data:
            assert data['_type'] in class_names, 'Encounter class type "%s" does not defined before' % data['_type']
            _type = data.pop('_type')
            return class_names[_type](**data)

        return data

    return object_hook

def get_json_encoder(classes):
    """
        Get custom json encoder that can encode provided classes.

        @param classes list<PYTHON_CLASS>
    """
    return type('CustomJSONEncoder', (DynamicJSONEncoder,), dict(classes=classes))

def json_loads(data, classes):
    """
        Short hand for JSON loads
    """
    # warnings.warn('Stop using this short hand method, it has performance issue')
    return json.loads(data, object_hook=get_object_hook(classes))
