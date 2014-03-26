# Celery configuration file

""" For default worker: celery worker --purge -Q default -A logcrawler.tasks -P eventlet -c 500 -n default-worker
    For analyze worker: celery worker --purge -A logcrawler.tasks -Q analyze -n analyze-worker
""" 

from kombu import Exchange, Queue
from logcrawler.conf.config import CELERY_BROKER, CELERY_BACKEND, CELERY_WORKER_HOSTS


BROKER_URL = CELERY_BROKER
CELERY_RESULT_BACKEND = CELERY_BACKEND

CELERY_DISABLE_RATE_LIMITS = True

DEFAULT_QUEUE = (
    Queue('default', Exchange('default'), routing_key='default'),
)
ANALYZE_QUEUE = tuple([
    Queue(host, Exchange(host), routing_key=host) for host in CELERY_WORKER_HOSTS
])
CELERY_QUEUES = DEFAULT_QUEUE + ANALYZE_QUEUE


CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'default'
