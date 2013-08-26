#!/usr/bin/env python
# coding: utf-8

import os
import sys
import socket

from logcrawler import common
from logcrawler.spider import Spider
from logcrawler.analyzer import analyze
from logcrawler.conf import config, celeryconfig
from celery import Celery

logger = common.get_logger(filename=__file__)

celery = Celery('tasks')
celery.config_from_object(celeryconfig)

@celery.task
def download(url):
    try:
        pid = os.fork()
        if pid == 0:
            Spider(root=config.ROOT).crawl(url)
    except OSError, e:
        sys.stderr.write('fork subprocess failed: %d (%s)\n' % (e.errno, e.strerr))

@celery.task
def analyze_process(filename):
    return analyze(filename)
