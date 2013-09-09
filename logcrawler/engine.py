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
    def __init__(self, scheduler, download_callback=None, analyze_callback=None):

        self.download_callback = download_callback
        self.analyze_callback = analyze_callback

        self.checker = Thread(target=self.check)
        self.scheduler = scheduler
        self.scheduler.add_output_callback(self.put_task)

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
            url, deadline = task.get("url"), task.get("deadline")
            if url and self.download_callback:
                async_result = self.download_callback(url, deadline)
                self.put_result(async_result)
                LOG.info(msg="Download task [%s]" % url)

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
            self.put_result((None, None))

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

    def get_result(self, block=True, timeout=None):
        """ Get async result from result queue.
            By default, it will be blocked until new result is available.
        """
        try:
            result = self._result_queue.get(block=block, timeout=timeout)
        except Queue.Empty:
            return None
        self._result_queue.task_done()
        return result

    def put_result(self, result):
        """ Put async-result into result queue.
        """
        try:
            self._result_queue.put(result, block=False)
        except Queue.Full:
            LOG.warn(msg="put message to result queue: full")

    def check(self):
        """ Check result of download tasks.
        """
        LOG.info(msg="Start check thread [%d]" % get_ident())

        while not self._is_checker_stopped:
            async_result = self.get_result()

            if getattr(async_result, 'state', None) != 'SUCCESS':
                # task does not completed
                self.put_result(async_result)
                time.sleep(0.5)
                continue

            task_result = async_result.get()
            result, path, hostname = task_result['result'], task_result['local_path'], task_result['hostname']
            if result in ['success']:
                # task completed successfully
                if self.analyze_callback:
                    LOG.info(msg="Analyze %s on host %s" % (path, hostname))
                    self.analyze_callback(path, hostname)


class Scheduler(Cron):
    def __init__(self, task_creator, interval=30):
        super(Scheduler, self).__init__()
        self.add_job(interval, self.schedule)
        self.task_creator = task_creator
        self.task_creator.start()
        self.output_callback = None

    def add_output_callback(self, callback):
        self.output_callback = callback

    def stop(self):
        super(Scheduler, self).stop()
        self.task_creator.stop()

    def schedule(self):
        download_tasks = self.prepare()
        for task in download_tasks:
            real_task = {'url': task['src'], 'deadline': task['deadline']}
            self.output_callback(real_task)

    def prepare(self):
        download_tasks = self.task_creator.get_tasks()
        LOG.info(msg="schedule [%d] download tasks" % len(download_tasks))
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
