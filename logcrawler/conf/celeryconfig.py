# Celery configuration file

import socket
from logcrawler.conf.config import CELERY_BROKER, CELERY_BACKEND

BROKER_URL = CELERY_BROKER
CELERY_RESULT_BACKEND = CELERY_BACKEND
