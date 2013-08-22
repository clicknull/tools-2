#!/usr/bin/env python
#coding: UTF-8

"""
TaskFactory
    update configs once a minute by default,
    produce tasks with configs when get_tasks() called.

EXP:
factory = TaskFactory()
factory.start()
tasks = factory.get_tasks()
"""

import time
import threading

from logcrawler.conf import config
from logcrawler import common

LOG = common.get_logger(filename=__file__, topic=__file__)


class TaskFactory(threading.Thread):

    IDC_CONFIG_KEYS = frozenset([
        "id", "IDC_name", "IDC_ip_address_port", "service_name",
        "collect_interval_minutes", "delay_minutes", "max_delay_minutes",
        "status", "current_status",
        "description", "timestamp",
    ])

    def __init__(self, daemon=True, *args, **kwargs):
        super(TaskFactory, self).__init__(*args, **kwargs)
        self.daemon = daemon
        self.activate = True
        self._update_interval = 60  # seconds
        self._task_step = 60  # seconds
        self._flag = time.time()
        self._settings = []

    def get_tasks(self, timeflag=None):
        """timeflag: int
        """
        if timeflag is None:
            timeflag = time.time()

        tasktimes = self.get_tasks_times(timeflag)
        LOG.info(msg="got tasks times %s" % str(tasktimes))
        if tasktimes:
            self._flag = timeflag

        tasks = []
        for tasktime in tasktimes:
            for setting in self._settings:
                task = self.create_task(
                    usetime=tasktime, urlformat=config.DOWNLOAD_URL_FORMAT,
                    **setting)
                if task:
                    tasks.append(task)
        LOG.info(msg="got tasks %s" % str(tasks))
        return tasks

    def get_tasks_times(self, timeflag):
        segment_id = int(timeflag / self._task_step)
        segment_flag = int(self._flag / self._task_step)
        tasktimes = [id*self._task_step for id in range(segment_flag+1, segment_id+1)]
        return tasktimes

    def create_task(self, usetime, urlformat, **configs):
        """
        Args:
            usetime
            urlformat
            **configs as in self.IDC_CONFIG_KEYS
        """
        if self._illegal(configs):
            return {}

        task = {}
        if configs["status"]=="active" and configs["current_status"]=="online":
            delay = configs["delay_minutes"]
            maxdelay = configs["max_delay_minutes"]
            interval = configs["collect_interval_minutes"]
            if interval == 0:
                interval = 1

            urltime = usetime - delay*self._task_step
            YYYYmmddHHMM = time.strftime("%Y%m%d%H%M", time.localtime(urltime))
            configs["YYYYmmddHHMM"] = YYYYmmddHHMM
            configs["YYYYmmddHH"] = YYYYmmddHHMM[: -2]
            taskurl = str(urlformat % configs)

            if self._hit_sampling(urltime, interval):
                task["src"] = taskurl
                task["deadline"] = urltime + maxdelay*self._task_step
                LOG.info(msg="task[%s] created" % taskurl)
            else:
                LOG.info(msg="task[%s] skipped, sampling" % taskurl)
        return task

    def _illegal(self, configdict):
        if not set(configdict).issuperset(self.IDC_CONFIG_KEYS):
            LOG.warn(msg="config illegal: %s" % str(configdict))
            return True

        for key in ["delay_minutes", "max_delay_minutes"]:
            val = configdict[key]
            if not (isinstance(val, int) and val > 0):
                LOG.warn(msg="config illegal: %s" % key)
                return True

        interval = configdict["collect_interval_minutes"]
        if not (isinstance(interval, int) and interval >= 0):
            LOG.warn(msg="config illegal: collect_interval_minutes")
            return True

        return False

    def _hit_sampling(self, timestamp, interval):
        return int(timestamp / self._task_step) % interval == 0

    def run(self):
        while self.activate:
            time.sleep(self._update_interval)
            self.update_setting()

    def update_setting(self):
        iport = config.IDC_CONFIG_ADDRESS[0]  # need cacth exception here
        url = config.IDC_CONFIG_URL_FORMAT % iport

        LOG.info("request idc config from %s" % url)
        rest = common.RestWrapper()
        jsonobj = rest.get(url)
        LOG.info("got idc configs %s" % str(jsonobj))

        settings = extract_idc_settings(jsonobj)
        if settings:
            self._settings = settings

    def read_local(self):
        pass

    def save_to_local(self):
        pass

    def stop(self):
        self.activate = False


def extract_idc_settings(jsonobj):
    if (isinstance(jsonobj, dict) and
            jsonobj.get('status', 'nok') == 'ok' and
            isinstance(jsonobj.get('idc_collect', None), list)):
        return jsonobj['idc_collect']
    else:
        return []


def _test():
    factory = TaskFactory(daemon=False)
    factory.start()
    tasks = factory.get_tasks()


if __name__ == "__main__":
    _test()
