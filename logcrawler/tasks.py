#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
from celery import Celery

from logcrawler.spider import Spider
from logcrawler.analyzer import analyze as analyze_process
from logcrawler.conf import celeryconfig, config
from logcrawler import common


LOG = common.get_logger(filename=__file__, topic=__file__)

celery = Celery('tasks')
celery.config_from_object(celeryconfig)


@celery.task
def download(url, deadline, retry_delay=30, async=False):
    if async:
        # fork new process and exit parent
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            LOG.error(msg='fork subprocess failed: %d (%s)\n' % (e.errno, e.strerr))
            sys.exit(1)

    ret = Spider(root=config.ROOT).crawl(url)
    if ret['result'] in ['httperr', 'connecterr']:
        if deadline and deadline > time.time():
            # retry task with delay
            humanized_deadline = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(deadline))
            LOG.warning(msg='Retry donwload task [%s] with %ds, deadline %s' % (url, retry_delay, humanized_deadline))
            time.sleep(retry_delay)
            return download(url, deadline, retry_delay, False)
    return ret

@celery.task
def analyze(filename):
    return analyze_process(filename)


