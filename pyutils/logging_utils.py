#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import logging.config
import os

_logger = {'loggers': set(), 'handlers': {}}


def init_logging(config):
    # Update logging handlers
    deleting_handler_names = []
    new_handlers = []
    for handler_name in config.logging.handlers:
        handler = config.logging.handlers[handler_name]

        if handler_name.startswith('$rolling') and handler_name[-1] == '$':
            deleting_handler_names.append(handler_name)
            new_handlers.append(handler.to_dict())

    for name in deleting_handler_names:
        del config.logging.handlers[name]

    for new_handler in new_handlers:
        if new_handler['class'] == 'logging.FileHandler':
            # unroll file handler
            new_handler['class'] = [new_handler['class']] * len(new_handler['id'])
            for arg in ['formatter', 'level', 'mode', 'filename']:
                if isinstance(new_handler[arg], str):
                    new_handler[arg] = [new_handler[arg]] * len(new_handler['id'])
        else:
            # unroll console handler
            raise NotImplementedError('Not implement handler class: %s' % new_handler['class'])

        for i, handler_name in enumerate(new_handler['id']):
            handler = {}
            for arg in ['class', 'formatter', 'level', 'mode', 'filename']:
                handler[arg] = new_handler[arg][i]

            config.logging.handlers.set_conf(handler_name, handler, split_key=False)

    # Update logging logger
    deleting_logger_names = []
    new_loggers = []
    for logger_name in config.logging.loggers:
        if logger_name.startswith('$rolling') and logger_name[-1] == '$':
            deleting_logger_names.append(logger_name)
            new_loggers.append(config.logging.loggers[logger_name].to_dict())

    for logger_name in deleting_logger_names:
        del config.logging.loggers[logger_name]

    for new_logger in new_loggers:
        for arg in ['level', 'propagate']:
            if isinstance(new_logger[arg], (str, bool)):
                new_logger[arg] = [new_logger[arg]] * len(new_logger['id'])

        if isinstance(new_logger['handlers'][0], str):
            new_logger['handlers'] = [new_logger['handlers']] * len(new_logger['id'])

        for i, logger_name in enumerate(new_logger['id']):
            logger = {arg: new_logger[arg][i] for arg in ['level', 'propagate', 'handlers']}
            config.logging.loggers.set_conf(logger_name, logger, split_key=False)

    # Backup log file if needed
    for handler_name in config.logging.handlers:
        handler = config.logging.handlers[handler_name]

        if 'filename' in handler:
            if '__no_backup' in handler and handler.__no_backup:
                # only backup file when required, and the file must be not empty
                content = 0
                if os.path.exists(handler.filename.as_path()):
                    with open(handler.filename.as_path(), 'rb') as f:
                        content = len(f.read(5))  # read first 5 bytes to determine if file is empty or not
                if content > 0:
                    handler.filename.backup_path()

            if '__no_backup' in handler:
                del handler.__no_backup

            handler.filename.ensure_path_existence()


def get_logger(config, name):
    global _logger

    if name in _logger['loggers']:
        return logging.getLogger(name)

    dict_config = config.logging.to_dict()
    assert name in dict_config['loggers'], 'Undefined logger: %s' % name

    _logger['loggers'].add(name)

    logger_conf = dict_config['loggers'][name]

    logger = logging.getLogger(name)
    logger.propagate = logger_conf['propagate']
    # noinspection PyProtectedMember
    logger.setLevel(logging._checkLevel(logger_conf['level']))

    dict_configurator = logging.config.DictConfigurator(dict_config)

    formatters = dict_configurator.config.get('formatters', {})
    for fname in formatters:
        try:
            formatters[fname] = dict_configurator.configure_formatter(formatters[fname])
        except Exception as e:
            raise ValueError('Unable to configure formatter %r: %s' % (fname, e))

    for handler_name in dict_config['loggers'][name]['handlers']:
        if handler_name not in _logger['handlers']:
            # important to use configuration passed to dict_configurator instead of dict_config
            # because it has been processed to change file
            handler = dict_configurator.configure_handler(dict_configurator.config['handlers'][handler_name])

            _logger['handlers'][handler_name] = handler

        handler = _logger['handlers'][handler_name]
        logger.addHandler(handler)

    if 'filters' in logger_conf:
        raise NotImplementedError('Not support filters')

    return logger
