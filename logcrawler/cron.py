#!/usr/bin/env python
# coding: utf-8

""" Cron is a Unixcrond-like job executor based on separated thread.
    What's different about Unix crond is that it is periodically perform
    the job by interval instead of clock-driven.

    Usage:
        >>> def func(text): print text 
        >>> cron = Cron()
        >>> cron.add_job(2, func, ('hello',))
        >>> cron.run()

        >>> time.sleep(5)
        >>> cron.stop()
        
"""

from threading import Thread, Timer


class Cron(Thread):
    def __init__(self, *args, **kwargs):
        super(Cron, self).__init__(*args, **kwargs)
        self.daemon = True
        self.crontab = []

    def run(self):
        for job in self.crontab:
            job.do()

    def stop(self):
        for job in self.crontab:
            job.stop()

    def add_job(self, interval, callback, args=(), kwargs={}):
        job = CronJob(interval, callback, args, kwargs)
        if job not in self.crontab:
            self.crontab.append(job)


class CronJob:
    def __init__(self, interval, callback, args=(), kwargs={}):
        if interval <= 0:
            raise ValueError('invalid interval')
        self.interval = interval
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.timer = None

    def __eq__(self, other):
        return self.interval == other.interval and self.callback == other.callback and \
               self.args == other.args and self.kwargs == other.kwargs
    
    def wrap(self, *args, **kwargs):
        self.callback(*args, **kwargs)
        self.timer = Timer(self.interval, self.wrap, args, kwargs)
        self.timer.start()

    def do(self):
        self.wrap(*self.args, **self.kwargs)

    def stop(self):
        self.timer.cancel()
