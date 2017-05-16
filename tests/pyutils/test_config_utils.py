#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, uuid

from nose.tools import ok_, eq_

from pyutils.config_utils import load_config, write_config, StringConf, Configuration


def test_io():
    file_id = str(uuid.uuid4())
    config_file = f'/tmp/config_file_{file_id}.txt'
    ok_(not os.path.exists(config_file))

    # test load config from file
    with open(config_file, 'w') as f:
        content = f'''data:
    abc: ahe
    float: 6.1
    float_str: '6.1'
    int_str: '6'
dir:
    __workdir__: /home/ubuntu
    download: Downloads
'''
        f.write(content)

    config = load_config(config_file)
    ok_(config.data.abc == 'ahe')
    ok_(config.data.abc.as_path() == '/tmp/ahe')

    os.remove(config_file)

    # test save config to file
    ok_(not os.path.exists(config_file + '.backup'))
    write_config(config, config_file + '.backup')
    ok_(os.path.exists(config_file + '.backup'))
    with open(config_file + '.backup', 'r') as f:
        eq_(content, f.read())


def test_parsing_structure():
    file_id = str(uuid.uuid4())
    config_file = f'/tmp/config_file_{file_id}.txt'
    ok_(not os.path.exists(config_file))

    with open(config_file, 'w') as f:
        content = f'''data:
    abc: ahe
    float: 6.1
    float_str: '6.1'
    int_str: '6'
dir:
    __workdir__: /home/ubuntu
    download: Downloads
people:
  - name: peter
    mailbox: peter@hotmail.com
'''
        f.write(content)

    config = load_config(config_file)
    eq_(config.data.abc, 'ahe')
    eq_(config.data.abc.as_path(), '/tmp/ahe')
    eq_(config.data.float, 6.1)
    eq_(config.data.float_str, '6.1')
    eq_(config.data.float_str.as_float(), 6.1)
    eq_(config.data.int_str.as_int(), 6)
    eq_(config.data['abc'], 'ahe')
    eq_(config.get_conf('data.abc'), 'ahe')
    ok_(isinstance(config.people, list))
    ok_(isinstance(config.people[0], Configuration))
    eq_(config.people[0].mailbox, 'peter@hotmail.com')
    eq_(config.people[0].mailbox.as_path(), '/tmp/peter@hotmail.com')

    config.set_conf('data.test.abc', 5)
    eq_(config.data.test.abc, 5)


def test_dir_ops():
    file_id = str(uuid.uuid4())
    config_file = f'/tmp/config_file_{file_id}.txt'
    config_dir = f'/tmp/config_dir_{file_id}'
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

    config.config_dir.ensure_path_existence()
    ok_(os.path.exists(config_dir), 'Dir must exist')

    ok_(not os.path.exists(config_dir + '-1'), 'Dir must not exist')
    config.config_dir.backup_path()
    ok_(os.path.exists(config_dir + '-1'), 'Dir must exist')


def test_ref_ops():
    file_id = str(uuid.uuid4())
    config_file = f'/tmp/config_file_{file_id}.txt'
    ok_(not os.path.exists(config_file))

    with open(config_file, 'w') as f:
        f.write(f'''
logs:
    __workdir__: /home/peter
    expense: expense_sheets.csv
data:
    __workdir__: '/data'
    gold:
        monthly_expense: '@logs.expense'
        monthly_expense_path: '@@logs.expense'
    checklists:
        - '@logs.expense'
        - '@@logs.expense'
''')

    config = load_config(config_file)
    eq_(config.logs.expense, 'expense_sheets.csv')
    eq_(config.logs.expense.as_path(), '/home/peter/expense_sheets.csv')
    eq_(config.data.gold.monthly_expense, 'expense_sheets.csv')
    ok_(isinstance(config.data.gold.monthly_expense, StringConf))
    eq_(config.data.gold.monthly_expense.as_path(), '/home/peter/expense_sheets.csv')
    eq_(config.data.gold.monthly_expense_path, '/home/peter/expense_sheets.csv')
    ok_(isinstance(config.data.gold.monthly_expense_path, StringConf))
    eq_(config.data.checklists, [
        'expense_sheets.csv',
        '/home/peter/expense_sheets.csv'
    ])
    ok_(isinstance(config.data.checklists[0], StringConf))


def test_to_dict_ops():
    file_id = str(uuid.uuid4())
    config_file = f'/tmp/config_file_{file_id}.txt'
    ok_(not os.path.exists(config_file))

    with open(config_file, 'w') as f:
        f.write(f'''
logs:
    __workdir__: /home/peter
    expense: expense_sheets.csv
data:
    __workdir__: '/data'
    gold:
        monthly_expense: '@logs.expense'
        monthly_expense_path: '@@logs.expense'
''')

    config = load_config(config_file)
    eq_(config.data.to_dict(), {
        'gold': {
            'monthly_expense': 'expense_sheets.csv',
            'monthly_expense_path': '/home/peter/expense_sheets.csv',
        }
    })
