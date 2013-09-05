#!/usr/bin/env python
# coding: utf-8

import time
from celery import Celery

from logcrawler import common
from logcrawler.conf import celeryconfig


LOG = common.get_logger(filename=__file__, topic=__file__)


class Task(object):
    """ Creates new task from any callable.
    """

    celery = Celery('tasks')
    celery.config_from_object(celeryconfig)

    real_task = celery.task

    def __init__(self, func, **opts):
        self.func = self.wrap(func)
        self.opts = opts

    def __call__(self, *args, **kwargs):
        """ Asynchronous call function by celery task.
        """
        task_func = Task.real_task(self.func, **self.opts)
        return task_func.apply_async(args, kwargs)

    def wrap(self, func):
        def _wrap(*args, **kwargs):
            try:
                ret = func(*args, **kwargs)
            except RetryTaskError, e:
                if e.deadline and e.deadline > time.time():
                    time.sleep(e.delay)
                    return _wrap(*args, **kwargs)
            return ret
        return _wrap


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
