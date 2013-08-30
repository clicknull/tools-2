#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
from celery import Celery

from logcrawler import common
from logcrawler.spider import Spider
from logcrawler.analyzer import analyze
from logcrawler.conf import config, celeryconfig

LOG = common.get_logger(filename=__file__, topic=__file__)

class Task(object):
    """ Creates new task from any callable.
        Note: If async option is true, return value of the callbable function will be lost.
    """

    celery = Celery('tasks')
    celery.config_from_object(celeryconfig)

    real_task = celery.task

    def __init__(self, async=False, **opts):
        self.async = async
        self.opts = opts

    def __call__(self, func):
        def wrap(*args, **kwargs):
            new_func = self.async_wrap(func, args, kwargs) if self.async else func
            return Task.real_task(new_func, **self.opts)
        return wrap

    def async_wrap(self, func, args=(), kwargs={}):
        """ A asynchronous function wrapper based on independent process.
        """
        def wrap(*args, **kwargs):
            # fork new process and exit parent
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)
            except OSError, e:
                LOG.error(msg='fork subprocess failed: %d (%s)\n' % (e.errno, e.strerr))
                sys.exit(1)

            # run in child process
            try:
                func(*args, **kwargs)
            except RetryTaskError, e:
                if e.deadline and e.deadline > time.time():
                    time.sleep(e.delay)
                    func(*args, **kwargs)
        return wrap


class RetryTaskError(Exception):
    """ The task is to be retried later.
    """
    def __init__(self, message=None, delay=None, deadline=None):
        self.message = message
        self.delay = delay
        self.deadline = deadline
        Exception.__init__()

    def __str__(self):
        humanized_deadline = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.deadline))
        return 'Retry task {0} with {1}s, deadline {2}'.format(self.message, self.delay, humanized_deadline)
