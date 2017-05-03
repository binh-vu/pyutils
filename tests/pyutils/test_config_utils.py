#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time

from nose.tools import ok_
from pyutils.config_utils import load_config, write_config


def test_io():
    time_id = time.time()
    config_file = f'/tmp/config_file_{time_id}.txt'
    ok_(not os.path.exists(config_file))

    # test load config from file
    with open(config_file, 'w') as f:
        f.write('''
data:
    abc: ahe
    float: 6.1
    float_str: '6.1'
    int_str: '6'
''')
    config = load_config(config_file)
    ok_(config.data.abc == 'ahe')
    ok_(config.data.abc.as_path() == '/tmp/ahe')
    ok_(config.data.float == 6.1)
    ok_(config.data.float_str == '6.1')
    ok_(config.data.float_str.as_float() == 6.1)
    ok_(config.data.int_str.as_int() == 6)
    ok_(config.data['abc'] == 'ahe')
    ok_(config.get_conf('data.abc') == 'ahe')
    config.set_conf('data.test.abc', 5)
    ok_(config.data.test.abc == 5)

    os.remove(config_file)

    # test save config to file
    write_config(config, config_file)
    ok_(os.path.exists(config_file))


def test_dir_ops():
    time_id = time.time()
    config_file = f'/tmp/config_file_{time_id}.txt'
    config_dir = f'/tmp/config_dir_{time_id}'
    ok_(not os.path.exists(config_file))

    with open(config_file, 'w') as f:
        f.write(f'''
data:
    abc: ahe
    float: 6.1
    float_str: '6.1'
    int_str: '6'
config_dir: {config_dir}
''')

    config = load_config(config_file)
    ok_(config.config_dir == config_dir)
    ok_(not os.path.exists(config_dir), 'Dir must not exist')

    config.config_dir.ensure_dir_existence()
    ok_(os.path.exists(config_dir), 'Dir must exist')

    ok_(not os.path.exists(config_dir + '-1'), 'Dir must not exist')
    config.config_dir.backup_dir()
    ok_(os.path.exists(config_dir + '-1'), 'Dir must exist')