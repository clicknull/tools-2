#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import os
import gzip
import urllib2
import shutil
import traceback
import logging
import logging.handlers
import requests

from functools import wraps
from threading import Thread
from urlparse import urlunparse

from logcrawler.conf import config

CREATED_LOGNAMES = {}


def get_logger(filename=None, topic=None):
    """
    Return a logger syslog_handler(UDP) or file_handler or both.
        if filename is set, file_handler will be add,
        if topic is set, syslog_handler(UDP) will be add.

    Examples:
        1. get_logger(__file__)  # log into file
        2. get_logger(topic=__file__)  # log to syslog-ng
        3. get_logger(__file__, __file__)  # log into file and log to syslog-ng
        4. get_logger(filename=__file__, topic=__file__)  # same as 3.

        5. get_logger("/dir/test.py")
        6. get_logger(topic="test")
        7. get_logger(topic="/dir/test.py")
    """
    filename = logfilename(filename)
    topic = shortname(topic)
    return get_multilogger(topic=topic, filename=filename)


def get_multilogger(name=None, topic=None, filename=None,
                    level=config.LOG_LEVEL, *args, **kwargs):
    """
    get logger with syslog_handler(UDP) or file_handler or both.
    if it is not the first time to call this function with the same value of 'name',
    it will return the logger with the 'name' already created.

    Args:
        name: name of logger, default to topic, if not set and topic is None, set equal to filename
        topic: topic(program name) used by syslog reciever(EXP:syslog-ng)
        filename: name of local log file
        level: level of logger
        host: remote host(ip)
        port: remote port
        loglevel: log level
        format: format of log
        datefmt: format of date time in log

    Example:
        # log to syslog remote in default address
        log11 = get_multilogger(topic="test")
        log12 = get_multilogger(name="test", topic="test")

        # log to local file test.log
        log21 = get_multilogger(filename="test.log")
        log22 = get_multilogger(name="test", filename="test.log")

        # log to syslog remote and log to local file test.log
        log31 = get_multilogger(topic="test", filename="test.log")
        log32 = get_multilogger(name="test", topic="test", filename="test.log")

        get_multilogger(name="test_name", topic="test_topic",
                        level=logging.INFO, host="127.0.0.1", port=514)
    """
    if not name:
        name = topic if topic else filename
        if not name:
            name = None

    logger = logging.getLogger(name)
    if name in CREATED_LOGNAMES:
        print "logger of syslog[%s] in %s already created" % (name, __file__)
    else:
        CREATED_LOGNAMES[name] = None
        logger.setLevel(level)
        if topic:
            add_syslog_handler(logger=logger, topic=topic, *args, **kwargs)
        if filename:
            add_file_handler(logger=logger, filename=filename, *args, **kwargs)
    return logger


def add_syslog_handler(
        logger, topic,
        host=config.SYSLOG_HOST, port=config.SYSLOG_PORT,
        loglevel=config.LOG_LEVEL, format=config.LOG_FORMAT, datefmt=config.LOG_DATEFMT,
        *args, **kwargs):
    """
    Args:
        logger: instance of logger
        topic: topic used by syslog reciever(EXP:syslog-ng)
        host: remote host address
        port: remote port
        loglevel: log level
        format: format of log
        datefmt: format of date time in log

    Returns:
        handler: handler add

    Related syslog-ng setting:
        ###
        # destination d_localfile {
        #     file("/tmp/$PROGRAM.log", template("$MSG\n"));
        # };
        ###

    Example:
        import logging
        instance_of_logger = logging.getLogger()
        add_syslog_handler(instance_of_logger,
                           host="127.0.0.1", port=514, topic="test_topic")
    """
    prefix = topic + "[%(process)d]: "
    handler = logging.handlers.SysLogHandler(address=(host, port))
    handler.setLevel(loglevel)
    handler.setFormatter(logging.Formatter(fmt=prefix+format, datefmt=datefmt))
    logger.addHandler(handler)
    return handler


def add_stdout_handler(
        logger,
        loglevel=config.LOG_LEVEL, format=config.LOG_FORMAT, datefmt=config.LOG_DATEFMT,
        *args, **kwargs):
    """
    Args:
        logger: instance of logger
        loglevel: log level
        format: format of log
        datefmt: format of date time in log

    Returns:
        handler: handler add

    Example:
        import logging
        instance_of_logger = logging.getLogger()
        add_stdout_handler(instance_of_logger)
    """
    handler = logging.StreamHandler()
    handler.setLevel(loglevel)
    handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))
    logger.addHandler(handler)
    return handler


def add_file_handler(
        logger, filename,
        loglevel=config.LOG_LEVEL, format=config.LOG_FORMAT, datefmt=config.LOG_DATEFMT,
        *args, **kwargs):
    """
    Args:
        logger: instance of logger
        filename: name of log file
        loglevel: log level
        format: format of log
        datefmt: format of date time in log

    Returns:
        handler: handler add

    Example:
        import logging
        instance_of_logger = logging.getLogger()
        add_file_handler(instance_of_logger)
    """
    handler = logging.FileHandler(filename)
    handler.setLevel(loglevel)
    handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))
    logger.addHandler(handler)
    return handler


def shortname(fullname):
    """
    Example:
        shortname("/dir/name/test.py")  => will get =>  "test"
        shortname("/dir/test.py")  => will get =>  "test"
    """
    if isinstance(fullname, str):
        base = os.path.basename(fullname)
        short, suffix = os.path.splitext(base)
        return short
    else:
        return None


def logfilename(fullname, logdir=config.LOG_PARENT):
    """
    Example:
        logfilename("/dir/name/test.py", "/var/log")  => will get =>  "/var/log/test.log"
        logfilename("/dir/test.py", "/var/log/sub")  => will get =>  "/var/log/sub/test.log"
    """
    short = shortname(fullname)
    logname = None if short is None else os.path.join(logdir, short + ".log")
    return logname


def rename(old_path, new_path):
    if not os.path.exists(old_path):
        logging.error(msg="path %s doesn't exist" % old_path)
        return False

    new_path_parent = os.path.dirname(new_path.rstrip(os.sep))
    if new_path_parent == "":
        new_path_parent = "."

    # new_path中不能包含old_path(new_path, old_path均指其绝对路径)
    absolute_old_path = os.path.abspath(old_path)
    absolute_new_path_parent = os.path.abspath(new_path_parent)
    if absolute_new_path_parent.find(absolute_old_path) == 0:
        logging.error(msg="Old path [%s] is subpath of parent of newpath [%s]"
                      % (old_path, new_path))
        return False

    try:
        # 确保目标路径父目录存在
        if not os.path.exists(new_path_parent):
            makedirs(new_path_parent)
        os.rename(old_path, new_path)
    except OSError, error:
        logging.error(msg="Rename file %s error. catch exception %s:\n %s" %
                      (old_path, error, traceback.format_exc()))
        return False
    else:
        return True


def makedirs(path):
    if os.path.exists(path):
        return True

    try:
        os.makedirs(path)
    except os.error:
        logging.error(msg="make directory [%s] error." % path)
        return False
    else:
        return True

def remove(path):
    def exception_handler(function, path, excinfo):
        """this one is only a callback function. it's useless."""
        logging.error(msg="%s Remove %s failed,catch exception\n %s\n %s" %
                      (function, path, traceback.format_exc(), excinfo))

    if os.path.isdir(path):
        logging.info(msg="remove dir path %s." % (path,))
        shutil.rmtree(path, False, exception_handler)
    else:
        try:
            os.remove(path)
            logging.info(msg="remove file %s successfully." % (path,))
        except OSError, error:
            logging.error(msg="Remove %s failed, catch exception %s:\n %s" %
                          (path, error, traceback.format_exc()))

    if os.path.exists(path):
        return False
    else:
        return True


def async(func):
    """ Decorator for async call.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
    return wrapper
