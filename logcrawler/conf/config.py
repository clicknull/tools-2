#!/usr/bin/env python
# coding: utf-8

import os
import logging
import logging.handlers

try:
    from config_env import *
except ImportError:
    from config_env_alpha import *

# Target environment, must be in ['alpha', 'release']
# Not be used currently
ENV = 'alpha'

LOG_PARENT = "/var/log/logcrawler"
PID_PARENT = "/var/run/logcrawler"

if not os.path.exists(LOG_PARENT):
    os.makedirs(LOG_PARENT)
if not os.path.exists(PID_PARENT):
    os.makedirs(PID_PARENT)


# Log config
LOG_LEVEL   = logging.INFO
LOG_FORMAT  = "%(asctime)s %(levelname)s %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

SYSLOG_HOST = "192.168.111.214"
SYSLOG_PORT = 514

# ANALYZER_LOG_PATH  = os.path.join(LOG_PARENT, "analyzer.log")
# SCHEDULER_LOG_PATH = os.path.join(LOG_PARENT, "scheduler.log")
# ENGINE_LOG_PATH    = os.path.join(LOG_PARENT, "engine.log")
# SPIDER_LOG_PATH    = os.path.join(LOG_PARENT, "spider.log")


# Daemon config
DAEMON_PID    = os.path.join(PID_PARENT, "logcrawler.pid")
DAEMON_STDOUT = os.path.join(LOG_PARENT, "daemon.stdout")
DAEMON_STDERR = os.path.join(LOG_PARENT, "daemon.stderr")

# [engine]
DOWNLOAD_EXPIRE_SECONDS = 300
ANALYZE_EXPIRE_SECONDS = 300
TASK_RETRY_DELAY = 30


# [scheduler]
IDC_CONFIG_URL_FORMAT = "http://%(IP)s:%(PORT)s/_logcrawler/logcrawler_rest_api/IDC_collect/get/"
IDC_CONFIG_ADDRESS = [
    {"IP": REST_HOST, "PORT": REST_PORT},
    {"IP": "220.181.167.34", "PORT": "80"},
]
INTERVAL_MINUTES_DEFAULT = 1
DELAY_MINUTES_DEFAULT = 1
MAX_DELAY_MINUTES_DEFAULT = 5
DOWNLOAD_URL_FORMAT = TASK_SRC_FMT

# [tasks] Root directory of download save path.
ROOT = "/data2/web"
