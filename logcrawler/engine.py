#!/usr/bin/env python
# coding: utf-8

""" The logcrawler engine which controls the Scheduler, Spider and Analyzer.
"""

import Queue
import time
from threading import Thread, Timer
from thread import get_ident

from logcrawler.daemon import Daemon
from logcrawler.factory import TaskFactory
from logcrawler.probe import update_idc_current_status
from logcrawler.conf import config
from logcrawler.cron import Cron
from logcrawler import common, tasks


LOG = common.get_logger(filename=__file__, topic=__file__)


class Engine(object):
    def __init__(self, spider=None, analyzer=None, schedule_interval=30):
        self.executer = task_executer(spider, analyzer)

        self.checker = Thread(target=self.check)
        self.scheduler = Scheduler(interval=schedule_interval)
        self.scheduler.add_consumer_callback(self.put_task)

        self._is_stopped = True
        self._is_checker_stopped = True

        self._task_queue   = Queue.Queue()
        self._result_queue = Queue.Queue()
        self._timer = None

    def run(self):
        self._is_stopped = False

        self.start_scheduler()
        self.start_checker()

        while not self._is_stopped:
            task = self.get_task()
            task_result = self.perform_task(task)
            if task_result:
                self.put_task_result(task_result)

    def perform_task(self, task):
        """ Perform one task and return async task result.
        """
        url, deadline = task["url"], task["deadline"]
        if url:
            logger.info(msg="Download task [%s]" % url)
            return self.executer(url, deadline)
        else:
            return None

    def terminate(self):
        """ Terminate the engine.
        """
        self.stop_scheduler()
        self._task_queue.join()
        self._result_queue.join()
        self.stop_checker()

        self._is_stopped = True
        if self._timer:
            self._timer.cancel()

    def add_schedule_job(self, interval, callback, args=(), kwargs={}):
        self.scheduler.add_job(interval, callback, args, kwargs)

    def start_scheduler(self):
        LOG.info(msg="Start scheduler")
        self.scheduler.start()

    def stop_scheduler(self):
        self.scheduler.stop()

    def start_checker(self):
        self._is_checker_stopped = False
        self.checker.daemon = True
        self.checker.start()

    def stop_checker(self):
        self._is_checker_stopped = True
        # put dummy result to stop checker
        if self._result_queue.qsize() == 0:
            self.put_task_result(None)

    def get_task(self, block=True, timeout=300):
        try:
            task = self._task_queue.get(block=block, timeout=timeout)
        except Queue.Empty:
            LOG.warn(msg="get message from _task_queue: timeout")
            return {}
        self._task_queue.task_done()
        return task

    def put_task(self, task, delay=0, block=False):
        if delay <= 0:
            try:
                self._task_queue.put(task, block)
            except Queue.Full:
                LOG.warn(msg="reput failed: _task_queue is full")
        else:
            self._timer = Timer(delay, self._task_queue.put, [task, block])
            self._timer.start()

    def get_task_result(self, block=True, timeout=None):
        """ Get async result from result queue.
            By default, it will be blocked until new result is available.
        """
        try:
            result = self._result_queue.get(block=block, timeout=timeout)
        except Queue.Empty:
            return None
        self._result_queue.task_done()
        return result

    def put_task_result(self, result):
        """ Put async-result into result queue.
        """
        try:
            self._result_queue.put(result, block=False)
        except Queue.Full:
            LOG.warn(msg="put message to result queue: full")

    def filter_task_results(self):
        """ Get successful task result and discard failed task result.
        """
        success_results = []

        # FIXME: use yield
        for i in range(self._result_queue.qsize()):
            async_result = self.get_task_result()
            if async_result.state == 'SUCCESS':
                success_results.append(async_result)
            elif async_result.state == 'FAILURE':
                pass
            else:
                self.put_task_result(async_result)
        return success_results

    def check(self):
        """ Check result of download tasks.
        """
        LOG.info(msg="Start check thread [%d]" % get_ident())

        while not self._is_checker_stopped:
            for async_result in self.filter_task_results():
                download_result = async_result.get()
                result, path, hostname = download_result['result'], download_result['local_path'], download_result['hostname']
                if result in ['success']:
                    # do analyze
                    if self.analyze_callback:
                        LOG.info(msg="Analyze %s on host %s" % (path, hostname))
                        self.analyze_callback(path, hostname)
            time.sleep(0.1)


class Scheduler(Cron):
    def __init__(self, factory=None, interval=30):
        super(Scheduler, self).__init__()
        if factory:
            self.factory = factory
        else:
            self.factory = TaskFactory()
        self.factory.start()
        self.consumer_callback = None
        self.add_job(interval, self.schedule)

    def add_consumer_callback(self, callback):
        self.consumer_callback = callback

    def stop(self):
        super(Scheduler, self).stop()
        self.factory.stop()

    def schedule(self):
        download_tasks = self.prepare()
        for task in download_tasks:
            real_task = {'url': task['src'], 'deadline': task['deadline']}
            self.consumer_callback(real_task)

    def prepare(self):
        download_tasks = self.factory.get_tasks()
        logger.info(msg="schedule [%d] download tasks" % len(download_tasks))
        return download_tasks

def download(url, deadline):
    expires = config.DOWNLOAD_EXPIRE_SECONDS
    return tasks.download.apply_async(args=(url, deadline), expires=expires)

def analyze(filename, hostname):
    return tasks.analyze.apply_async(args=(filename,), queue=hostname, routing_key=hostname)

class EngineDaemon(Daemon):
    def run(self):
        factory = TaskFactory()
        scheduler = Scheduler(task_creator=factory, interval=30)
        engine = Engine(scheduler, download, analyze)
        engine.add_schedule_job(60, update_idc_current_status)
        engine.run()
