#!/usr/bin/env python
# coding: utf-8

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
    return Spider(root=config.ROOT).crawl(url)

@celery.task
def analyze_process(filename):
    logger.info(msg="analyze_process request.delivery_info %s" % analyze_process.request.delivery_info)
    logger.info(msg="analyze_process filename %s" % filename)
    return analyze(filename)
